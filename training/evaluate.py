"""Score a model on data/eval/*.jsonl with the same decision logic a router would use in production.

  python training/evaluate.py --model models/laya_onnx --name baseline         # ONNX dir (laya.onnx + tokenizer.json + rl_agent_config.json)
  python training/evaluate.py --model runs/student150/best --name student150_dev  # torch checkpoint (MPS)

Every message is asked against its workflow's full path list through `LayaModel.choose` (prompt, cuts,
temperature buckets, softmax) and `decision` (choice==__none__ -> no_match; best < thr -> below_threshold;
else matched). A torch checkpoint dir (has model.safetensors) runs through the same class with `_run`
swapped for a torch forward.

Writes reports/<name>.md, reports/<name>.json and reports/<name>.preds.jsonl.
"""

import argparse
import collections
import glob
import json
import math
import os
import sys
import time
from types import SimpleNamespace

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import HISTORY_HINT, INSTRUCTIONS, NONE, OPTION_FORMATS, Encoder, build_criteria, no_match_key  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

THRESHOLDS = [round(0.4 + 0.05 * i, 2) for i in range(11)]
PROD_THRESHOLD = 0.6  # default match threshold
MIN_TEMPERATURE, MAX_TEMPERATURE = 0.5, 5.0


def _clamp(temperature):
    return min(MAX_TEMPERATURE, max(MIN_TEMPERATURE, float(temperature)))


def _softmax(z):
    p = np.exp(z - z.max())
    return p / p.sum()


class LayaModel:
    """ONNX chooser: laya.onnx + tokenizer.json + rl_agent_config.json in one dir, onnxruntime on CPU."""

    def __init__(self, model_dir, threads=4):
        import onnxruntime as ort
        from tokenizers import Tokenizer

        self.tokenizer = Tokenizer.from_file(os.path.join(model_dir, "tokenizer.json"))
        self._configure(json.load(open(os.path.join(model_dir, "rl_agent_config.json"))))
        self.threads = threads
        opts = ort.SessionOptions()
        opts.intra_op_num_threads, opts.inter_op_num_threads = threads, 1
        self.session = ort.InferenceSession(os.path.join(model_dir, "laya.onnx"), sess_options=opts,
                                            providers=["CPUExecutionProvider"])

    def _configure(self, cfg):
        self.max_len, self.head_max_len = cfg.get("max_len", 512), cfg.get("head_max_len", 192)
        self.option_format = cfg.get("option_format", "prod")
        self.default_temperature = _clamp(cfg.get("temperature", [1.0])[0])
        self.temperatures = {k: _clamp(v) for k, v in cfg.get("temperature_by_options", {}).items()}

    def choose(self, state, instructions, criteria):
        """Answer the Choice question: `choice`, `probabilities`, `confidence` and `degraded`."""
        keys = list(criteria)
        ids, markers, degraded = self._encode(state, instructions, criteria)
        logits = self._run(ids, markers)[: len(keys)]
        probs = _softmax(logits / self._temperature(len(keys)))
        entropy = -(probs * np.log(np.clip(probs, 1e-12, 1.0))).sum()
        return SimpleNamespace(
            choice=keys[int(probs.argmax())],
            probabilities={k: float(p) for k, p in zip(keys, probs, strict=True)},
            confidence=float(np.clip(1.0 - entropy / math.log(len(keys)), 0.0, 1.0)),
            degraded=degraded,
        )

    def _encode(self, state, instructions, criteria):
        """Encoder layout plus the list of cuts made to fit (phrasings, message, many paths)."""
        enc = self._enc
        options, cut = enc.options(criteria, report=True)
        head_room = self.head_max_len - sum(map(len, options))
        head = enc._tokens(f"choice question: {instructions}")[: max(8, head_room)]
        ids = [enc.cls, *head, enc.sep]
        markers = []
        for option in options:
            markers.append(len(ids))
            ids += option
        ids.append(enc.sep)
        state_room = max(0, self.max_len - len(ids) - 1)
        state_ids = enc._tokens(json.dumps(state, ensure_ascii=False))
        ids = (ids + state_ids[:state_room] + [enc.sep])[: self.max_len]
        markers = [m for m in markers if m < self.max_len]
        if len(markers) != len(options):
            raise ValueError(f"options exceed max_len={self.max_len}")
        degraded = [f"phrasings_cut paths={cut} tokens_per_path={min(len(o) - 1 for o in options)}"] if cut else []
        if len(state_ids) > state_room:
            degraded.append(f"message_cut tokens={len(state_ids)} kept={state_room}")
        if len(options) > 10:
            degraded.append(f"many_paths paths={len(options) - 1} (past 10 options the temperature is uncalibrated)")
        return ids, markers, degraded

    def _run(self, ids, markers):
        inputs = {"input_ids": np.array([ids], dtype=np.int64), "attention_mask": np.ones((1, len(ids)), dtype=np.int64),
                  "marker_pos": np.array([markers], dtype=np.int64), "marker_mask": np.ones((1, len(markers)), dtype=bool),
                  "qtype": np.array([0], dtype=np.int64)}  # 0 = choice question
        return self.session.run(["logits"], inputs)[0][0]

    def _temperature(self, n):
        bucket = "2" if n <= 2 else "3-5" if n <= 5 else "6-10" if n <= 10 else "11+"
        return self.temperatures.get(f"choice:{bucket}", self.default_temperature)


def set_format(model, option_format):
    """Prompt `model` in `option_format` (after any head_max_len override)."""
    model.option_format = option_format
    model._enc = Encoder(model.tokenizer, model.max_len, model.head_max_len, option_format)


class TorchLaya(LayaModel):
    """LayaModel with the ONNX session replaced by a torch checkpoint (laya.Agent layout)."""

    def __init__(self, ckpt_dir, device, net=None, cfg=None, tokenizer_json=None):
        """From a checkpoint dir, or (net, cfg, tokenizer_json) to wrap a model already in memory (train.py's
        --select_metric intent). The caller puts an in-memory net back in train() mode afterwards."""
        import torch
        from tokenizers import Tokenizer

        self.torch, self.device = torch, device
        if net is None:
            from train import load_checkpoint
            net, cfg, d = load_checkpoint(ckpt_dir)
            net.to(device)
            tokenizer_json = os.path.join(d, "tokenizer", "tokenizer.json")
        self.net = net.eval()
        self.tokenizer = Tokenizer.from_file(tokenizer_json)
        self._configure(cfg)
        self.threads = None

    def _run(self, ids, markers):
        t, dev = self.torch, self.device
        with t.no_grad():
            lg = self.net(input_ids=t.tensor([ids], device=dev), attention_mask=t.ones((1, len(ids)), dtype=t.long, device=dev),
                          marker_pos=t.tensor([markers], device=dev), marker_mask=t.ones((1, len(markers)), dtype=t.bool, device=dev),
                          qtype=t.zeros(1, dtype=t.long, device=dev))[0]
        return lg[0].float().cpu().numpy()


def dir_size(path):
    return sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(path) for f in fs)


def ask(model, paths, message, history=None, shortlister=None, k=0):
    """One Choice question. With a shortlister and len(paths) > k, only the top-k paths (+ __none__) reach the
    chooser: none_key comes from the full list, and every path that was not shortlisted gets probability 0,
    so `probabilities` still covers every path. ms includes the shortlist."""
    intents = [p["path_id"] for p in paths]
    none_key = no_match_key(paths)
    state = {"message": message, **({"history": list(history)} if history else {})}
    instr = INSTRUCTIONS + (HISTORY_HINT if history else "")
    t0 = time.perf_counter()
    kept = shortlister.shortlist(message, paths, k) if shortlister and k else paths
    sl_ms = (time.perf_counter() - t0) * 1000
    crit = build_criteria(kept, none_key, model.option_format)
    ans = model.choose(state, instr, crit)
    enc = model._enc  # share of path-option tokens (key + phrasings) that reached the chooser (compact formats)
    if model.option_format != "prod":
        opts = enc.options(crit)[0][:-1]
        need = [len(enc._tokens(f" {k}: {d}")) for k, d in list(crit.items())[:-1]]
        ans.tokens_kept = sum(min(len(o) - 1, n) for o, n in zip(opts, need)) / max(1, sum(need))
    if len(kept) < len(paths):
        pr = ans.probabilities
        ans.probabilities = {**{p["path_id"]: pr.get(p["path_id"], 0.0) for p in paths}, none_key: pr[none_key]}
    ms = (time.perf_counter() - t0) * 1000
    ans.kept, ans.shortlist_ms = [p["path_id"] for p in kept], sl_ms
    return ans, intents, none_key, ms


def load_model(path, threads=4, device=None, option_format=None, head_max_len=None):
    """ONNX dir (CPU, `threads` intra_op) or torch checkpoint dir (device, default mps) -> (model, backend, size_bytes),
    with optional option_format / head_max_len overrides applied. Shared with training/dynamic_eval.py."""
    if os.path.exists(os.path.join(path, "laya.onnx")):
        backend = f"onnx cpu intra_op={threads}"
        model = LayaModel(path, threads)
        size = dir_size(path)
    else:
        import torch
        dev = device or ("mps" if torch.backends.mps.is_available() else "cpu")
        backend = f"torch {dev}"
        model = TorchLaya(path, dev)
        size = os.path.getsize(os.path.join(path, "model.safetensors"))
    if head_max_len:
        model.head_max_len = head_max_len
    set_format(model, option_format or model.option_format)
    return model, backend, size


def record(ans, intents, none_key, ms, gold, model=None, thresholds=None):
    """One scored question (the output of `ask`) -> prediction dict with router decisions per threshold."""
    gold_key = none_key if gold == NONE else gold
    p = {"choice": ans.choice, "probs": ans.probabilities, "confidence": ans.confidence, "degraded": ans.degraded,
         "ms": round(ms, 1), "n_tokens": getattr(model, "last_len", None),
         "argmax_ok": ans.choice == gold_key, "_intents": intents, "_none_key": none_key,
         "n_chooser_paths": len(ans.kept), "gold_shortlisted": gold == NONE or gold in ans.kept,
         "shortlist_ms": round(ans.shortlist_ms, 2),
         "tokens_kept": round(getattr(ans, "tokens_kept", float("nan")), 4)}
    p["dec"] = {t: decide(p, t) for t in (thresholds or THRESHOLDS)}
    return p


def decision(choice, probabilities, path_ids, none_key, thr):
    """Router decision: declining is no_match, the best path under thr is below_threshold, else matched."""
    scores = [probabilities[k] for k in path_ids if k in probabilities]
    if choice == none_key:
        return "no_match"
    return "below_threshold" if not scores or max(scores) < thr else "matched"


def decide(p, thr):
    """Decision for a stored prediction at another threshold."""
    return decision(p["choice"], p["probs"], p["_intents"], p["_none_key"], thr)


def ece(conf, correct, bins=15):
    edges, e = np.linspace(0, 1, bins + 1), 0.0
    for i, (lo, hi) in enumerate(zip(edges[:-1], edges[1:])):
        sel = ((conf >= lo) if i == 0 else (conf > lo)) & (conf <= hi)
        if sel.any():
            e += sel.mean() * abs(conf[sel].mean() - correct[sel].mean())
    return float(e)


def group_metrics(ps, thr):
    """Metrics for one slice. Rates are None when the slice has no member of that kind."""
    def rate(sel, ok):
        sel = list(sel)
        return round(sum(map(ok, sel)) / len(sel), 4) if sel else None
    none = [p for p in ps if p["gold"] == NONE]
    ins = [p for p in ps if p["gold"] != NONE]
    ok_at = lambda p: (p["dec"][thr] != "matched") if p["gold"] == NONE else (p["dec"][thr] == "matched" and p["choice"] == p["gold"])
    conf = np.array([max(p["probs"].values()) for p in ps])
    corr = np.array([p["argmax_ok"] for p in ps], dtype=float)
    return {
        "n": len(ps), "n_none": len(none),
        "acc": rate(ps, lambda p: p["argmax_ok"]),                  # argmax (incl. __none__) == gold
        f"acc@{thr}": rate(ps, ok_at),                               # end-to-end routing correct
        "path_acc": rate(ins, lambda p: p["argmax_ok"]),             # in-scope argmax == gold
        f"path_acc@{thr}": rate(ins, ok_at),                         # in-scope matched to the right path
        f"none_recall@{thr}": rate(none, lambda p: p["dec"][thr] != "matched"),
        "none_recall_argmax": rate(none, lambda p: p["choice"] == p["_none_key"]),
        f"false_accept@{thr}": rate(none, lambda p: p["dec"][thr] == "matched"),
        "ece": round(ece(conf, corr), 4) if ps else None,
    }


def decision_table(ps):
    rows = []
    none = [p for p in ps if p["gold"] == NONE]
    ins = [p for p in ps if p["gold"] != NONE]
    f = lambda sel, ok: round(sum(map(ok, sel)) / len(sel), 4) if sel else None
    for t in THRESHOLDS:
        rows.append({
            "threshold": t,
            "acc": f(ps, lambda p: (p["dec"][t] != "matched") if p["gold"] == NONE else (p["dec"][t] == "matched" and p["choice"] == p["gold"])),
            "inscope_matched_right": f(ins, lambda p: p["dec"][t] == "matched" and p["choice"] == p["gold"]),
            "inscope_matched_wrong": f(ins, lambda p: p["dec"][t] == "matched" and p["choice"] != p["gold"]),
            "inscope_no_match": f(ins, lambda p: p["dec"][t] == "no_match"),
            "inscope_below_threshold": f(ins, lambda p: p["dec"][t] == "below_threshold"),
            "none_recall": f(none, lambda p: p["dec"][t] != "matched"),
            "false_accept": f(none, lambda p: p["dec"][t] == "matched"),
        })
    return rows


def pct(ms, q):
    return round(float(np.percentile(ms, q)), 1) if ms else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="ONNX dir (laya.onnx + tokenizer.json + rl_agent_config.json) or torch checkpoint dir")
    ap.add_argument("--name", required=True)
    ap.add_argument("--eval", default=os.path.join(ROOT, "data", "eval", "*.jsonl"),
                    help="glob; the default suite skips large_nodes.jsonl (score it with --eval data/eval/large_nodes.jsonl)")
    ap.add_argument("--shortlist_k", type=int, default=0, help="shortlist mode: nodes with > k paths send only the top-k paths + __none__ to the chooser (0 = off)")
    ap.add_argument("--embedder", default=os.path.join(ROOT, "models", "embed", "bge-small"), help="shortlist embedder dir (training/shortlist.py)")
    ap.add_argument("--shortlist_agg", choices=["max", "top2"], default="max")
    ap.add_argument("--threads", type=int, default=4, help="onnxruntime intra_op threads")
    ap.add_argument("--device", default=None, help="torch backend device (default mps if available)")
    ap.add_argument("--threshold", type=float, default=PROD_THRESHOLD, help="headline threshold (default 0.6)")
    ap.add_argument("--option_format", choices=list(OPTION_FORMATS), default=None, help="override the model's option_format (zero-shot format tests)")
    ap.add_argument("--head_max_len", type=int, default=None, help="override the model's head_max_len")
    ap.add_argument("--limit", type=int, default=0, help="messages per file (0 = all); for smoke runs")
    a = ap.parse_args()
    thr = a.threshold
    THRESHOLDS.append(thr) if thr not in THRESHOLDS else None

    t0 = time.perf_counter()
    model, backend, size = load_model(a.model, a.threads, a.device, a.option_format, a.head_max_len)
    run = model._run

    def counted_run(ids, markers):  # record prompt length per question (latency proxy)
        model.last_len = len(ids)
        return run(ids, markers)
    model._run = counted_run
    load_s = time.perf_counter() - t0

    files = sorted(glob.glob(a.eval))
    if a.eval == ap.get_default("eval"):
        files = [f for f in files if not f.endswith("large_nodes.jsonl")]
    shortlister = None
    if a.shortlist_k:
        from shortlist import Embedder, Shortlister
        shortlister = Shortlister(Embedder(a.embedder, threads=a.threads), agg=a.shortlist_agg)
    first = files and json.loads(open(files[0]).readline())
    try:
        _, _, _, first_ms = ask(model, first["paths"], first["messages"][0]["text"], None, shortlister, a.shortlist_k)  # cold first call
    except ValueError:  # first node does not fit the chooser; warm up on a tiny question instead
        _, _, _, first_ms = ask(model, first["paths"][:2], first["messages"][0]["text"])

    preds, workflows, errors = [], [], {}
    for fp in files:
        fname = os.path.basename(fp).removesuffix(".jsonl")
        for line in open(fp):
            wf = json.loads(line)
            cut_msgs = 0
            msgs = wf["messages"][: a.limit] if a.limit else wf["messages"]
            for m in msgs:
                try:
                    ans, intents, none_key, ms = ask(model, wf["paths"], m["text"], m.get("history"), shortlister, a.shortlist_k)
                except ValueError as e:  # "options exceed max_len": the node does not fit the chooser at all
                    errors[wf["workflow_id"]] = str(e)
                    break
                p = {"file": fname, "workflow_id": wf["workflow_id"], "n_paths": len(wf["paths"]), "text": m["text"],
                     "gold": m["gold"], "tags": m["tags"], **record(ans, intents, none_key, ms, m["gold"], model)}
                cut_msgs += any(d.startswith("phrasings_cut") for d in ans.degraded)
                preds.append(p)
            if wf["workflow_id"] in errors:
                print(f"{wf['workflow_id']}: skipped, {errors[wf['workflow_id']]}", file=sys.stderr)
                preds = [p for p in preds if p["workflow_id"] != wf["workflow_id"]]
                continue
            workflows.append({"file": fname, "workflow_id": wf["workflow_id"], "paths": len(wf["paths"]),
                              "phrasings": sum(len(p["text"]) for p in wf["paths"]), "messages": len(msgs),
                              "phrasings_cut_msgs": cut_msgs,
                              "degraded_example": next((d for p in preds[-len(msgs):] for d in p["degraded"]), None)})
        print(f"{fname}: {sum(p['file'] == fname for p in preds)} msgs", file=sys.stderr)

    if not preds:
        sys.exit(f"no questions scored; every node was skipped: {errors}")
    by_file = collections.defaultdict(list)
    by_tag = collections.defaultdict(list)
    by_wf = collections.defaultdict(list)
    for p in preds:
        by_file[p["file"]].append(p)
        by_wf[p["workflow_id"]].append(p)
        for t in p["tags"]:
            by_tag[t].append(p)
        by_tag["__none__ (all)" if p["gold"] == NONE else "in_scope (all)"].append(p)

    seven = [p["ms"] for p in preds if p["n_paths"] == 7]
    lat = {"backend": backend, "load_s": round(load_s, 2), "first_call_ms": round(first_ms, 1),
           "p50_7path_ms": pct(seven, 50), "p95_7path_ms": pct(seven, 95), "max_7path_ms": pct(seven, 100), "n_7path": len(seven),
           "p50_all_ms": pct([p["ms"] for p in preds], 50), "p95_all_ms": pct([p["ms"] for p in preds], 95),
           "max_all_ms": pct([p["ms"] for p in preds], 100)}
    report = {
        "name": a.name, "model": os.path.abspath(a.model), "backend": backend,
        "option_format": model.option_format, "head_max_len": model.head_max_len, "max_len": model.max_len,
        "mean_tokens": round(float(np.mean([p["n_tokens"] for p in preds])), 1),
        "mean_tokens_7path": round(float(np.mean([p["n_tokens"] for p in preds if p["n_paths"] == 7] or [0])), 1), "size_bytes": size, "threshold": thr,
        "overall": group_metrics(preds, thr),
        "by_file": {k: group_metrics(v, thr) for k, v in sorted(by_file.items())},
        "by_tag": {k: group_metrics(v, thr) for k, v in sorted(by_tag.items())},
        "by_workflow": {k: {"paths": v[0]["n_paths"], **group_metrics(v, thr),
                            "shortlist_recall": round(float(np.mean([p["gold_shortlisted"] for p in v if p["gold"] != NONE] or [1])), 4),
                            "p50_ms": pct([p["ms"] for p in v], 50), "p95_ms": pct([p["ms"] for p in v], 95),
                            "p95_shortlist_ms": pct([p["shortlist_ms"] for p in v], 95)} for k, v in sorted(by_wf.items())},
        "shortlist": {"k": a.shortlist_k, "embedder": a.embedder if a.shortlist_k else None, "agg": a.shortlist_agg if a.shortlist_k else None},
        "errors": errors,
        "decision_table": decision_table(preds),
        "decision_table_by_file": {k: decision_table(v) for k, v in sorted(by_file.items())},
        "latency": lat,
        "workflows": workflows,
        "tokens_kept_rate": round(float(np.nanmean([p["tokens_kept"] for p in preds])), 4),
        "shortlist_recall": round(float(np.mean([p["gold_shortlisted"] for p in preds if p["gold"] != NONE] or [1])), 4),
        "phrasings_cut_rate": round(sum(any(d.startswith("phrasings_cut") for d in p["degraded"]) for p in preds) / len(preds), 4),
    }
    os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
    base = os.path.join(ROOT, "reports", a.name)
    json.dump(report, open(base + ".json", "w"), indent=1)
    with open(base + ".preds.jsonl", "w") as f:
        for p in preds:
            f.write(json.dumps({k: v for k, v in p.items() if not k.startswith("_")}) + "\n")
    open(base + ".md", "w").write(to_md(report))
    print(to_md(report))


def table(rows, cols):
    fmt = lambda v: "" if v is None else (f"{v:.3f}" if isinstance(v, float) else str(v))
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(fmt(r.get(c)) for c in cols) + " |" for r in rows]
    return "\n".join(out)


def to_md(r):
    t = r["threshold"]
    cols = ["slice", "n", "n_none", "acc", f"acc@{t}", "path_acc", f"path_acc@{t}", f"none_recall@{t}",
            "none_recall_argmax", f"false_accept@{t}", "ece"]
    lat = r["latency"]
    md = [f"# Eval: {r['name']}", "",
          f"Model `{r['model']}`, backend {r['backend']}, size on disk {r['size_bytes'] / 1e6:.0f} MB. "
          f"Prompt: option_format {r.get('option_format', 'prod')}, head_max_len {r.get('head_max_len')}, max_len {r.get('max_len')}; "
          f"mean {r.get('mean_tokens')} tokens per question ({r.get('mean_tokens_7path')} on 7-path). "
          f"Headline threshold {t}. Built by `training/evaluate.py`.", "",
          "- `acc`: argmax over paths + `__none__` equals gold. `acc@t`: end-to-end routing is right at threshold t "
          "(a path message is `matched` to its path; a `__none__` message is `no_match` or `below_threshold`).",
          "- `path_acc`: the same, on in-scope messages only. `none_recall@t`: `__none__` messages not matched. "
          "`none_recall_argmax`: `__none__` won the argmax. `false_accept@t` = 1 - none_recall@t. "
          "ECE: 15 bins over max probability vs argmax correctness.", "",
          "## Overall and per file", "",
          table([{"slice": "**all**", **r["overall"]}] + [{"slice": k, **v} for k, v in r["by_file"].items()], cols), "",
          "## Per tag", "", table([{"slice": k, **v} for k, v in r["by_tag"].items()], cols), "",
          "## Decision table (router decision logic, all files)", "",
          table(r["decision_table"], list(r["decision_table"][0])), "",
          "## Per workflow", "",
          (f"Shortlist mode: k={r['shortlist']['k']}, embedder `{r['shortlist']['embedder']}`, agg {r['shortlist']['agg']}. "
           if r.get("shortlist", {}).get("k") else "Full-list mode (no shortlist). ")
          + "`shortlist_recall`: in-scope messages whose gold path reached the chooser; ms includes the shortlist."
          + (f" Skipped (does not fit the chooser): {r['errors']}" if r.get("errors") else ""), "",
          table([{"slice": k, **v} for k, v in r["by_workflow"].items()],
                ["slice", "paths", "n", "n_none", "acc", f"acc@{t}", "path_acc", f"none_recall@{t}", "ece", "shortlist_recall",
                 "p50_ms", "p95_ms", "p95_shortlist_ms"]), ""]
    for k, v in r["decision_table_by_file"].items():
        md += [f"### {k}", "", table(v, ["threshold", "acc", "inscope_matched_right", "inscope_matched_wrong", "none_recall",
                                         "false_accept"]), ""]
    md += ["## Latency", "",
           f"Backend {lat['backend']}. Load {lat['load_s']} s, first (cold) call {lat['first_call_ms']} ms. "
           f"7-path questions (n={lat['n_7path']}): p50 {lat['p50_7path_ms']} ms, p95 {lat['p95_7path_ms']} ms, "
           f"max {lat['max_7path_ms']} ms. All questions: p50 {lat['p50_all_ms']} ms, p95 {lat['p95_all_ms']} ms, "
           f"max {lat['max_all_ms']} ms.", "",
           "## Input cuts per workflow", "",
           f"`phrasings_cut` on {r['phrasings_cut_rate']:.1%} of questions; path-option tokens kept {r.get('tokens_kept_rate', float('nan')):.1%}; shortlist recall {r.get('shortlist_recall', 1):.4f}.", "",
           table(r["workflows"], ["file", "workflow_id", "paths", "phrasings", "messages", "phrasings_cut_msgs", "degraded_example"]), ""]
    return "\n".join(md)


if __name__ == "__main__":
    main()
