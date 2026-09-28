"""Single-device (MPS/CPU/CUDA) Laya fine-tune + distillation, adapted from the official
notebook's train_ddp.py (soft-target CE + optional proper-scoring policy-gradient, encoder/head
LR split, held-out temperature refit). Prompt format = training/common.py.

  teacher:  python training/train.py --mode teacher --train T.jsonl --dev D.jsonl --out runs/teacher
  label:    python training/train.py --mode label --init runs/teacher/best --train T.jsonl --out T.teacher.jsonl
  student:  python training/train.py --mode student --encoder jhu-clsp/ettin-encoder-150m \
                --train T.jsonl --distill_file T.teacher.jsonl --dev D.jsonl --out runs/student
  calibrate: python training/train.py --mode calibrate --init runs/student/best --dev D.jsonl

Output dirs (best/, last/) use the laya.Agent layout: model.safetensors, rl_agent_config.json,
tokenizer/, encoder/config.json. last/ also holds trainer_state.pt for --resume.
"""

import argparse
import json
import logging
import math
import os
import random
import shutil
import sys
import time

import numpy as np
import torch
from safetensors.torch import load_file, save_file

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import NONE, OPTION_FORMATS, Encoder, load_tokenizer  # noqa: E402

from laya.agent import _fix_tokenizer_config  # noqa: E402
from laya.common import TEMP_MAX, TEMP_MIN, build_model, ece_score, proper_reward, temp_bucket  # noqa: E402

log = logging.getLogger("train")
BUCKETS = ("choice:2", "choice:3-5", "choice:6-10", "choice:11+")


# ---------------------------------------------------------------- data

def read_jsonl(path):
    """Episodes; workflow records ({workflow_id, paths, messages:[{text,gold,tags}]}) are flattened.
    A comma-joined path reads each file in turn (e.g. train.jsonl,train_sl.jsonl)."""
    if "," in path:
        return [e for p in path.split(",") for e in read_jsonl(p)]
    out = []
    with open(path) as f:
        for n, line in enumerate(f):
            if not line.strip():
                continue
            r = json.loads(line)
            if "messages" in r:
                for i, m in enumerate(r["messages"]):
                    out.append({"id": f"{r['workflow_id']}:{i}", "paths": r["paths"], "message": m["text"],
                                "history": m.get("history"), "gold": m["gold"], "domain": r.get("domain")})
            else:
                r.setdefault("id", f"{os.path.basename(path)}:{n}")
                out.append(r)
    return out


def attach_teacher(eps, path):
    tp = {r["id"]: r["teacher_probs"] for r in read_jsonl(path) if "teacher_probs" in r}
    missing = sum(e["id"] not in tp for e in eps)
    for e in eps:
        if e["id"] in tp:
            e["teacher_probs"] = tp[e["id"]]
    log.info("teacher probs for %d/%d episodes (%d missing -> gold only)", len(eps) - missing, len(eps), missing)


def make_batches(eps, enc, micro_batch, max_tokens, rng):
    """Length-bucketed batches: sort pools of 50 batches by length, cut, shuffle batch order."""
    order = list(range(len(eps)))
    rng.shuffle(order)
    batches, pool = [], micro_batch * 50
    for s in range(0, len(order), pool):
        chunk = sorted(order[s:s + pool], key=lambda i: eps[i]["_len"])
        cur = []
        for i in chunk:
            if cur and (len(cur) >= micro_batch or (len(cur) + 1) * max(eps[i]["_len"], eps[cur[0]]["_len"]) > max_tokens):
                batches.append(cur)
                cur = []
            cur.append(i)
        if cur:
            batches.append(cur)
    rng.shuffle(batches)
    return batches


def collate(items, pad_id, device):
    n, L, K = len(items), max(len(it["ids"]) for it in items), max(len(it["markers"]) for it in items)
    ids = torch.full((n, L), pad_id, dtype=torch.long)
    att = torch.zeros((n, L), dtype=torch.long)
    mpos = torch.zeros((n, K), dtype=torch.long)
    mmask = torch.zeros((n, K), dtype=torch.bool)
    target = torch.zeros((n, K))
    for i, it in enumerate(items):
        ids[i, :len(it["ids"])] = torch.tensor(it["ids"])
        att[i, :len(it["ids"])] = 1
        k = len(it["markers"])
        mpos[i, :k] = torch.tensor(it["markers"])
        mmask[i, :k] = True
        target[i, :k] = torch.tensor(it["target"])
    b = {"input_ids": ids, "attention_mask": att, "marker_pos": mpos, "marker_mask": mmask,
         "qtype": torch.zeros(n, dtype=torch.long)}
    return {k: v.to(device) for k, v in b.items()}, target.to(device)


def with_target(it, alpha):
    """Training target = alpha * teacher + (1 - alpha) * one-hot gold (soft CE on it == alpha*KL + (1-alpha)*CE + const)."""
    gold = [0.0] * len(it["keys"])
    gold[it["label"]] = 1.0
    t = it.get("target")
    it["target"] = [alpha * a + (1 - alpha) * g for a, g in zip(t, gold)] if t and alpha > 0 else gold
    return it


# ---------------------------------------------------------------- model io

def resolve_dir(path_or_id):
    if os.path.isdir(path_or_id):
        return path_or_id
    from huggingface_hub import snapshot_download
    return snapshot_download(path_or_id, allow_patterns=["rl_agent_config.json", "model.safetensors", "tokenizer/*", "encoder/*"])


def load_checkpoint(path_or_id):
    d = resolve_dir(path_or_id)
    _fix_tokenizer_config(d)
    cfg = json.load(open(os.path.join(d, "rl_agent_config.json")))
    model = build_model(cfg, encoder_dir=os.path.join(d, "encoder"), pretrained=False)
    model.load_state_dict({k: v.float() for k, v in load_file(os.path.join(d, "model.safetensors")).items()}, strict=True)
    return model, cfg, d


def save_checkpoint(model, cfg, tok_src_dir, out, extra=None, half=False):
    """Atomic write of a laya.Agent-loadable dir (+ optional trainer state)."""
    tmp = out + ".tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(os.path.join(tmp, "tokenizer"))
    sd = {k: (v.half() if half and v.is_floating_point() else v).detach().contiguous().cpu() for k, v in model.state_dict().items()}
    save_file(sd, os.path.join(tmp, "model.safetensors"))
    model.encoder.config.save_pretrained(os.path.join(tmp, "encoder"))
    for f in ("tokenizer.json", "tokenizer_config.json", "special_tokens_map.json"):
        if os.path.exists(os.path.join(tok_src_dir, f)):
            shutil.copy(os.path.join(tok_src_dir, f), os.path.join(tmp, "tokenizer", f))
    json.dump(cfg, open(os.path.join(tmp, "rl_agent_config.json"), "w"), indent=2)
    if extra is not None:
        torch.save(extra, os.path.join(tmp, "trainer_state.pt"))
    shutil.rmtree(out, ignore_errors=True)
    os.rename(tmp, out)


# ---------------------------------------------------------------- eval / calibration

@torch.no_grad()
def predict(model, enc, eps, device, batch_size=16):
    """Raw logits per episode (natural path order, as production sends them)."""
    model.eval()
    items = [enc.encode(e) for e in eps]
    order = sorted(range(len(items)), key=lambda i: len(items[i]["ids"]))
    out = [None] * len(items)
    for s in range(0, len(order), batch_size):
        idx = order[s:s + batch_size]
        b, _ = collate([with_target(dict(items[i]), 0.0) for i in idx], enc.pad, device)
        lg = model(**b)[0].float().cpu().numpy()
        for r, i in enumerate(idx):
            out[i] = lg[r, :len(items[i]["markers"])]
    return items, out


def softmax(z):
    p = np.exp(z - z.max())
    return p / p.sum()


def metrics(items, logits, temps=None):
    n = len(items)
    corr, conf, nll, none_tot, none_ok, fa = [], [], 0.0, 0, 0, 0
    for it, z in zip(items, logits):
        k = len(z)
        t = (temps or {}).get(temp_bucket(0, k), 1.0)
        p = softmax(z / t)
        pred = int(p.argmax())
        corr.append(float(pred == it["label"]))
        conf.append(float(p.max()))
        nll -= math.log(max(p[it["label"]], 1e-12))
        gold_none = it["label"] == k - 1
        none_tot += gold_none
        none_ok += gold_none and pred == k - 1
        fa += gold_none and pred != k - 1 and p[pred] >= 0.6  # engine would wrongly route at its 0.6 threshold
    return {"n": n, "acc": sum(corr) / max(1, n), "nll": nll / max(1, n),
            "ece": ece_score(np.array(conf), np.array(corr)) if n else float("nan"),
            "none_recall": none_ok / max(1, none_tot), "false_accept@0.6": float(fa) / max(1, none_tot)}


def fit_one_temp(sel):
    """Recipe's LBFGS fit of one temperature on (logits, one-hot/soft target) pairs."""
    if len(sel) < 10:
        return None
    kmax = max(len(z) for z, _ in sel)
    Z = torch.full((len(sel), kmax), -1e4)
    T = torch.zeros((len(sel), kmax))
    for i, (z, t) in enumerate(sel):
        Z[i, :len(z)] = torch.tensor(z)
        T[i, :len(t)] = torch.tensor(t, dtype=torch.float32)
    log_t = torch.zeros(1, requires_grad=True)
    opt = torch.optim.LBFGS([log_t], lr=0.1, max_iter=100)

    def closure():
        opt.zero_grad()
        loss = -(T * torch.log_softmax(Z / log_t.exp(), -1)).sum(-1).mean()
        loss.backward()
        return loss
    opt.step(closure)
    return min(TEMP_MAX, max(TEMP_MIN, log_t.exp().item()))  # production clamps to [0.5, 5] anyway


def refit_temperature(cfg, items, logits):
    sel = [(z, np.eye(len(z))[it["label"]]) for it, z in zip(items, logits)]
    glob = fit_one_temp(sel) or 1.0
    tbo = {k: v for k, v in cfg.get("temperature_by_options", {}).items() if not k.startswith("choice:")}
    for b in BUCKETS:
        tbo[b] = fit_one_temp([s for s in sel if temp_bucket(0, len(s[0])) == b]) or glob
    t = list(cfg.get("temperature", [1.0, 1.0, 1.0]))
    t[0] = glob
    cfg["temperature"], cfg["temperature_by_options"] = t, tbo
    counts = {b: sum(temp_bucket(0, len(z)) == b for z in logits) for b in BUCKETS}
    log.info("temperatures: global=%.3f %s (n per bucket %s; <10 -> global)", glob,
             {b: round(tbo[b], 3) for b in BUCKETS}, counts)
    return cfg


def calibrate_dir(ckpt_dir, calib_eps, device):
    model, cfg, _ = load_checkpoint(ckpt_dir)
    model.to(device)
    enc = Encoder.from_cfg(load_tokenizer(os.path.join(ckpt_dir, "tokenizer", "tokenizer.json")), cfg)
    items, logits = predict(model, enc, calib_eps, device)
    log.info("calib before: %s", metrics(items, logits))
    cfg = refit_temperature(cfg, items, logits)
    log.info("calib after:  %s", metrics(items, logits, cfg["temperature_by_options"]))
    json.dump(cfg, open(os.path.join(ckpt_dir, "rl_agent_config.json"), "w"), indent=2)
    del model


# ---------------------------------------------------------------- main

def parse():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["teacher", "student", "label", "calibrate"], required=True)
    ap.add_argument("--init", default="convaiinnovations/laya", help="teacher init / checkpoint for label+calibrate")
    ap.add_argument("--encoder", default="jhu-clsp/ettin-encoder-150m", help="student backbone (HF id)")
    ap.add_argument("--train"), ap.add_argument("--dev"), ap.add_argument("--calib", help="calibration jsonl (default: held-out slice of --train)")
    ap.add_argument("--distill_file", help="jsonl with {id, teacher_probs} (from --mode label)")
    ap.add_argument("--alpha", type=float, default=0.7, help="student: weight of teacher probs vs gold one-hot")
    ap.add_argument("--out", required=False)
    ap.add_argument("--epochs", type=float, default=2)
    ap.add_argument("--max_steps", type=int, default=0, help="optimizer updates; overrides --epochs when >0")
    ap.add_argument("--micro_batch", type=int, default=8)
    ap.add_argument("--max_tokens", type=int, default=4096, help="cap on micro_batch * padded_len")
    ap.add_argument("--grad_accum", type=int, default=4)
    ap.add_argument("--lr_encoder", type=float, default=None, help="default teacher 2.5e-5 (recipe), student 5e-5")
    ap.add_argument("--lr_head", type=float, default=None, help="default teacher 1e-4 (recipe), student 3e-4")
    ap.add_argument("--warmup", type=float, default=0.06)
    ap.add_argument("--rl_weight", type=float, default=1.0, help="recipe's policy-gradient term; 0 = soft CE only")
    ap.add_argument("--sigma_start", type=float, default=0.4), ap.add_argument("--sigma_end", type=float, default=0.1)
    ap.add_argument("--group_size", type=int, default=4)
    ap.add_argument("--amp", choices=["none", "bf16", "fp16"], default="none", help="fp32 is fastest on M2 MPS")
    ap.add_argument("--grad_ckpt", action=argparse.BooleanOptionalAction, default=None, help="default on for teacher, off for student")
    ap.add_argument("--shuffle_paths", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--eval_every", type=int, default=200)
    ap.add_argument("--dev_max", type=int, default=2000)
    ap.add_argument("--calib_max", type=int, default=2000)
    ap.add_argument("--option_format", choices=list(OPTION_FORMATS), default=None, help="teacher/student: prompt option format (default: init's, else prod)")
    ap.add_argument("--head_max_len", type=int, default=None, help="teacher/student: head token budget (default: init's, 192)")
    ap.add_argument("--select_metric", choices=["acc", "intent"], default="acc",
                    help="best/ by dev acc, or by the dynamic dev-intent score (training/dynamic_eval.py --dev_intent)")
    ap.add_argument("--select_every", type=int, default=0, help="intent: score every N updates (default --eval_every)")
    ap.add_argument("--select_shortlist_k", type=int, default=4, help="intent: shortlist k of the dev-intent draw (0 = full list)")
    ap.add_argument("--select_calib_max", type=int, default=1000, help="intent: calib episodes for the temperature refit before scoring")
    ap.add_argument("--select_scale", type=float, default=1.0, help="intent: size of the dev-intent draw (smoke runs)")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--seed", type=int, default=20260926)
    ap.add_argument("--device", default="mps" if torch.backends.mps.is_available() else "cpu")
    return ap.parse_args()


def setup_logging(path=None):
    handlers = [logging.StreamHandler(sys.stdout)]
    if path:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        handlers.append(logging.FileHandler(path))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", handlers=handlers, force=True)


def mem_gb():
    return torch.mps.driver_allocated_memory() / 1e9 if torch.backends.mps.is_available() else 0.0


def main():
    a = parse()
    device = torch.device(a.device)

    if a.mode == "calibrate":
        setup_logging()
        calibrate_dir(a.init, read_jsonl(a.calib or a.dev), device)
        return

    if a.mode == "label":  # teacher soft probs (calibrated temps) -> {id, teacher_probs}
        setup_logging()
        model, cfg, d = load_checkpoint(a.init)
        model.to(device)
        enc = Encoder.from_cfg(load_tokenizer(os.path.join(d, "tokenizer", "tokenizer.json")), cfg)
        eps = read_jsonl(a.train)
        done = {json.loads(l)["id"] for l in open(a.out)} if os.path.exists(a.out) else set()  # resume
        if done:
            log.info("resuming: %d already labelled", len(done))
            eps = [e for e in eps if e["id"] not in done]
        temps = cfg.get("temperature_by_options", {})
        with open(a.out, "a") as f:
            for s in range(0, len(eps), 512):
                items, logits = predict(model, enc, eps[s:s + 512], device)
                for e, it, z in zip(eps[s:s + 512], items, logits):
                    p = softmax(z / min(TEMP_MAX, max(TEMP_MIN, temps.get(temp_bucket(0, len(z)), 1.0))))
                    keys = it["keys"][:-1] + [NONE]  # production always puts the none option last
                    f.write(json.dumps({"id": e["id"], "teacher_probs": {k: round(float(v), 6) for k, v in zip(keys, p)},
                                        "teacher_logits": [round(float(v), 4) for v in z]}) + "\n")  # raw, same order as keys
                f.flush()
                log.info("labelled %d/%d", min(s + 512, len(eps)), len(eps))
        return

    os.makedirs(a.out, exist_ok=True)
    setup_logging(os.path.join(a.out, "train.log"))
    log.info("args %s", vars(a))
    torch.manual_seed(a.seed)
    teacher = a.mode == "teacher"
    lr_enc = a.lr_encoder or (2.5e-5 if teacher else 5e-5)
    lr_head = a.lr_head or (1e-4 if teacher else 3e-4)
    grad_ckpt = teacher if a.grad_ckpt is None else a.grad_ckpt

    # model + tokenizer
    if teacher:
        model, cfg, init_dir = load_checkpoint(a.init)
        tok_dir = os.path.join(init_dir, "tokenizer")
    else:
        base_cfg = json.load(open(os.path.join(resolve_dir("convaiinnovations/laya"), "rl_agent_config.json")))
        cfg = {k: base_cfg[k] for k in ("head_layers", "max_len", "head_max_len", "max_prefixes", "act_costs", "cost_wrong_act")}
        cfg.update(encoder=a.encoder, model_name="laya-student", amp_dtype="bf16", temperature=[1.0, 1.0, 1.0])
        model = build_model(cfg, pretrained=True)  # HF encoder weights + fresh head (same architecture)
        from huggingface_hub import snapshot_download
        tok_dir = snapshot_download(a.encoder, allow_patterns=["tokenizer.json", "tokenizer_config.json", "special_tokens_map.json"])
    cfg["option_format"] = a.option_format or cfg.get("option_format", "prod")
    if a.head_max_len:
        cfg["head_max_len"] = a.head_max_len
    model.encoder.config.reference_compile = False
    enc = Encoder.from_cfg(load_tokenizer(os.path.join(tok_dir, "tokenizer.json")), cfg)
    if grad_ckpt:
        model.encoder.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        model.head_checkpointing = True
    model.to(device).train()
    log.info("model %s | params %.1fM | grad_ckpt=%s | option_format %s head_max_len %d max_len %d", cfg["encoder"],
             sum(p.numel() for p in model.parameters()) / 1e6, grad_ckpt, cfg["option_format"], cfg["head_max_len"], cfg["max_len"])

    # data
    eps = read_jsonl(a.train)
    if a.distill_file:
        attach_teacher(eps, a.distill_file)
    if a.calib:
        calib_eps = read_jsonl(a.calib)
    else:  # recipe: hold a fixed calibration slice out of training
        order = list(range(len(eps)))
        random.Random(20260922).shuffle(order)
        n_cal = min(a.calib_max, len(eps) // 10)
        calib_eps, eps = [eps[i] for i in order[:n_cal]], [eps[i] for i in order[n_cal:]]
    dev_eps = read_jsonl(a.dev)[: a.dev_max] if a.dev else []
    for e in eps:
        e["_len"] = len(enc.encode(e)["ids"])
    log.info("train %d | calib %d | dev %d | mean len %.0f | max len %d", len(eps), len(calib_eps), len(dev_eps),
             np.mean([e["_len"] for e in eps]), max(e["_len"] for e in eps))

    # optimizer (recipe: AdamW, wd 0.01, encoder/head LR split) + warmup-cosine
    enc_p = [p for n, p in model.named_parameters() if n.startswith("encoder.")]
    head_p = [p for n, p in model.named_parameters() if not n.startswith("encoder.")]
    opt = torch.optim.AdamW([{"params": enc_p, "lr": lr_enc}, {"params": head_p, "lr": lr_head}], weight_decay=0.01)
    per_epoch = math.ceil(len(make_batches(eps, enc, a.micro_batch, a.max_tokens, random.Random(0))) / a.grad_accum)
    total = a.max_steps or max(1, int(per_epoch * a.epochs))
    warm = max(1, int(total * a.warmup))
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: min(1.0, (s + 1) / warm) * (0.04 + 0.96 * 0.5 * (1 + math.cos(math.pi * min(1.0, s / total)))))
    amp = {"bf16": torch.bfloat16, "fp16": torch.float16}.get(a.amp)
    scaler = torch.amp.GradScaler(device.type, enabled=a.amp == "fp16")

    step, epoch, skip, best = 0, 0, 0, -1.0
    last_dir, best_dir = os.path.join(a.out, "last"), os.path.join(a.out, "best")
    if a.resume and os.path.exists(os.path.join(last_dir, "trainer_state.pt")):
        st = torch.load(os.path.join(last_dir, "trainer_state.pt"), weights_only=False)
        model.load_state_dict({k: v.to(device) for k, v in load_file(os.path.join(last_dir, "model.safetensors")).items()})
        opt.load_state_dict(st["opt"])
        sched.load_state_dict(st["sched"])
        step, epoch, skip, best = st["step"], st["epoch"], st["batch_in_epoch"], st["best"]
        random.setstate(st["py_rng"])
        log.info("resumed at step %d (epoch %d, batch %d, best %.4f)", step, epoch, skip, best)
    log.info("updates %d (%d/epoch) | warmup %d | micro %d x accum %d | lr enc %.1e head %.1e | rl_weight %.2f | amp %s",
             total, per_epoch, warm, a.micro_batch, a.grad_accum, lr_enc, lr_head, a.rl_weight, a.amp)

    def evaluate():
        if not dev_eps:
            return None
        items, logits = predict(model, enc, dev_eps, device)
        model.train()
        return metrics(items, logits)

    def intent_score():
        """Dev-intent score of the live model at production decision logic. Temperatures are refit on a calib slice
        first (a copy of cfg), so acc@0.6 / none_recall@0.6 mean what they will after the final refit."""
        import copy
        import dynamic_eval
        t = time.time()
        tcfg = copy.deepcopy(cfg)
        if calib_eps:
            items, logits = predict(model, enc, calib_eps[: a.select_calib_max], device)
            refit_temperature(tcfg, items, logits)
        live = dynamic_eval.live_model(model, tcfg, os.path.join(tok_dir, "tokenizer.json"), device)
        score, s = dynamic_eval.dev_intent(live, shortlist_k=a.select_shortlist_k, scale=a.select_scale)
        model.train()
        acc = {k: v[f"acc@{dynamic_eval.ev.PROD_THRESHOLD}"] for k, v in s["probes"].items()}
        log.info("  dev_intent %.4f | worst %s %.4f | %s | %.0fs", score, s["worst_probe"], s["worst_acc"], acc, time.time() - t)
        return score

    def checkpoint(bi, m, intent=None):
        nonlocal best
        if a.select_metric == "intent":  # intent is None when the draw was not due: only last/ is written
            score, improve = intent, intent is not None and intent > best
        else:
            score = m["acc"] if m else -step  # no dev -> "best" = latest
            improve = m is None or score > best
        if improve:
            best = score
            save_checkpoint(model, cfg, tok_dir, best_dir, half=False)
            log.info("  new best %.4f -> %s", best, best_dir)
        save_checkpoint(model, cfg, tok_dir, last_dir, extra={
            "opt": opt.state_dict(), "sched": sched.state_dict(), "step": step, "epoch": epoch,
            "batch_in_epoch": bi, "best": best, "py_rng": random.getstate()})

    aug = random.Random(a.seed)
    t0, tl, seen, loss_acc, peak = time.time(), time.time(), 0, 0.0, 0.0
    done = step >= total
    while not done:
        batches = make_batches(eps, enc, a.micro_batch, a.max_tokens, random.Random(a.seed + epoch))
        opt.zero_grad(set_to_none=True)
        for bi in range(skip, len(batches)):
            chunk = [with_target(enc.encode(eps[i], aug if a.shuffle_paths else None), 0.0 if teacher else a.alpha)
                     for i in batches[bi]]
            b, target = collate(chunk, enc.pad, device)
            with torch.autocast(device.type, dtype=amp) if amp else torch.autocast(device.type, enabled=False):
                logits, _ = model(**b)
            logits = logits.float()
            mask = b["marker_mask"]
            loss = -(target * torch.log_softmax(logits.masked_fill(~mask, -1e4), -1)).sum(-1).mean()
            if a.rl_weight > 0:  # recipe: Gaussian logit-noise policy gradient on a proper scoring reward
                sigma = a.sigma_start + (a.sigma_end - a.sigma_start) * min(1.0, step / total)
                k = mask.sum(-1, keepdim=True).float()
                eps_ = torch.randn((a.group_size,) + logits.shape, device=device) * sigma * mask
                eps_ = (eps_ - eps_.sum(-1, keepdim=True) / k) * mask
                z = logits.detach().unsqueeze(0) + eps_
                with torch.no_grad():
                    q = torch.softmax(z.masked_fill(~mask, -1e4), -1)
                    r = proper_reward(q, target.unsqueeze(0), b["qtype"], mask, w_sph=0.75, w_rps=1.0)
                    adv = (r - r.mean(0, keepdim=True)) / ((r - r.mean(0, keepdim=True)).std() + 1e-6)
                logp = -(((z - logits.unsqueeze(0)) ** 2) * mask).sum(-1) / (2 * sigma ** 2)
                loss = loss + a.rl_weight * -(adv * logp).mean()
            scaler.scale(loss / a.grad_accum).backward()
            loss_acc += loss.item()
            seen += 1
            if (bi + 1) % a.grad_accum and bi + 1 < len(batches):
                continue
            scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(opt)
            scaler.update()
            sched.step()
            opt.zero_grad(set_to_none=True)
            step += 1
            peak = max(peak, mem_gb())
            if step % 10 == 0 or step == total:
                if device.type == "mps":
                    torch.mps.synchronize()
                dt = time.time() - tl
                log.info("step %d/%d ep %d | loss %.4f | %.2fs/update | lr %.2e | mps %.1fGB peak %.1fGB",
                         step, total, epoch, loss_acc / max(1, seen), dt / 10, sched.get_last_lr()[0], mem_gb(), peak)
                tl, loss_acc, seen = time.time(), 0.0, 0
            due_sel = a.select_metric == "intent" and (step % (a.select_every or a.eval_every) == 0 or step >= total)
            if step % a.eval_every == 0 or step >= total or due_sel:
                m = evaluate()
                if m:
                    log.info("  dev %s", {k: round(v, 4) for k, v in m.items()})
                checkpoint(bi + 1, m, intent_score() if due_sel else None)
                tl = time.time()  # keep eval/save time out of s/update
            if step >= total:
                done = True
                break
        skip = 0
        epoch += 1

    log.info("training done in %.1f min", (time.time() - t0) / 60)
    del opt
    model.cpu()
    if device.type == "mps":
        torch.mps.empty_cache()
    if calib_eps:
        calibrate_dir(best_dir, calib_eps, device)
        shutil.copy(os.path.join(best_dir, "rl_agent_config.json"), os.path.join(last_dir, "rl_agent_config.json"))
    log.info("best -> %s", best_dir)


if __name__ == "__main__":
    main()
