"""Zero-shot intent router: pick which of your paths a message belongs to, or none of them.

    from router import Router
    r = Router.from_pretrained()          # or Router("path/to/local/dir")
    r.route("i want to cancel my order 88213", {
        "order_status": ["Customer wants to know where their order is"],
        "cancel_order": ["Customer wants to cancel an existing order"],
    })
    # {'match': 'cancel_order', 'score': 0.97, 'probabilities': {...}}

Needs: pip install onnxruntime tokenizers numpy huggingface_hub
"""

import hashlib
import json
import os
import re
from collections import OrderedDict

import numpy as np

REPO_ID = "vrajnotviraj/laya-intent-router-150m-onnx"
INSTRUCTIONS = (
    "A user sent this message to a conversational workflow that branches into the paths below. "
    "Which path is the message asking for?"
)
HISTORY_HINT = (
    " `history` holds the earlier turns of this conversation, oldest first; a short or elliptical "
    "message usually continues the intent of the most recent turns."
)
NO_MATCH_DESCRIPTION = "Gibberish, filler words, or a message unrelated to every other path."
NONE = "__none__"
OPTION_CAP, MIN_HEAD_TOKENS, PHRASING_SEP = 96, 16, '" | "'


def _water_fill(lengths, budget, floor=4):
    open_ = list(range(len(lengths)))
    while open_:
        fair = budget // len(open_)
        short = [i for i in open_ if lengths[i] <= fair]
        if not short:
            break
        budget -= sum(lengths[i] for i in short)
        open_ = [i for i in open_ if lengths[i] > fair]
    alloc = list(lengths)
    for j, i in enumerate(open_):
        alloc[i] = max(floor, budget // len(open_) + (j < budget % len(open_)))
    return alloc


def _humanise(path_id):
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", path_id)
    return re.sub(r"[_\-.:/]+", " ", s).strip().lower()


def _session(path, threads):
    import onnxruntime as ort

    o = ort.SessionOptions()
    o.intra_op_num_threads, o.inter_op_num_threads = threads, 1
    return ort.InferenceSession(path, o, providers=["CPUExecutionProvider"])


class Shortlist:
    """bge-small embedder: keeps the k paths closest to the message (best phrasing wins). Cached per path set."""

    def __init__(self, model_dir, threads=4, cache_size=512):
        from tokenizers import Tokenizer

        self.tok = Tokenizer.from_file(os.path.join(model_dir, "tokenizer.json"))
        self.tok.enable_truncation(128)
        self.tok.enable_padding(pad_id=self.tok.token_to_id("[PAD]") or 0)
        self.sess = _session(os.path.join(model_dir, "model.onnx"), threads)
        self.cache, self.cache_size = OrderedDict(), cache_size

    def _embed(self, texts):
        encs = self.tok.encode_batch(texts)
        ids = np.array([e.ids for e in encs], dtype=np.int64)
        mask = np.array([e.attention_mask for e in encs], dtype=np.int64)
        v = self.sess.run(None, {"input_ids": ids, "attention_mask": mask, "token_type_ids": np.zeros_like(ids)})[0][:, 0]
        return v / np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-8)

    def top(self, message, paths, k):
        key = hashlib.blake2b(json.dumps(paths).encode(), digest_size=16).hexdigest()
        if key not in self.cache:
            texts, owner = [], []
            for j, texts_j in enumerate(paths.values()):
                for t in list(texts_j) + [_humanise(list(paths)[j])]:
                    texts.append(t)
                    owner.append(j)
            self.cache[key] = (self._embed(texts), np.array(owner))
            if len(self.cache) > self.cache_size:
                self.cache.popitem(last=False)
        self.cache.move_to_end(key)
        vecs, owner = self.cache[key]
        sims = vecs @ self._embed([message])[0]
        best = np.array([sims[owner == j].max() for j in range(len(paths))])
        keep = set(np.argsort(-best, kind="stable")[:k].tolist())
        return {p: t for j, (p, t) in enumerate(paths.items()) if j in keep}


class Router:
    def __init__(self, model_dir, threads=4, shortlist_k=4):
        from tokenizers import Tokenizer

        self.cfg = json.load(open(os.path.join(model_dir, "rl_agent_config.json")))
        self.tok = Tokenizer.from_file(os.path.join(model_dir, "tokenizer.json"))
        self.cls, self.sep, self.mask = (self.tok.token_to_id(t) for t in ("[CLS]", "[SEP]", "[MASK]"))
        self.sess = _session(os.path.join(model_dir, "laya.onnx"), threads)
        self.threshold = self.cfg.get("match_threshold", 0.625)
        self.temps = self.cfg["temperature_by_options"]
        sl_dir = os.path.join(model_dir, "shortlist")
        self.k = shortlist_k if os.path.isdir(sl_dir) else 0
        self.shortlist = Shortlist(sl_dir, threads) if self.k else None

    @classmethod
    def from_pretrained(cls, repo_id=REPO_ID, **kw):
        from huggingface_hub import snapshot_download

        return cls(snapshot_download(repo_id), **kw)

    def _tokens(self, text):
        return self.tok.encode(text.replace("[MASK]", " "), add_special_tokens=False)

    def _options(self, criteria, head_max_len):
        texts = [f" {k}: {d}".replace("[MASK]", " ") for k, d in criteria.items()]
        encs = [self.tok.encode(t, add_special_tokens=False) for t in texts]
        options = [[self.mask] + e.ids[:OPTION_CAP] for e in encs]
        if head_max_len - sum(map(len, options)) < MIN_HEAD_TOKENS:  # too many paths: share the budget fairly
            alloc = _water_fill([len(o) for o in options], head_max_len - MIN_HEAD_TOKENS)
            for i, (t, e, a) in enumerate(zip(texts, encs, alloc)):
                n = a - 1
                if n >= len(options[i]) - 1:
                    continue
                ends, keep = [end for _, end in e.offsets], n
                p = t.find(PHRASING_SEP)
                while p >= 0:  # prefer cutting between phrasings
                    b = sum(x <= p + 1 for x in ends)
                    if b > n:
                        break
                    if 4 * (n - b) <= a:
                        keep = b
                    p = t.find(PHRASING_SEP, p + 1)
                options[i] = [self.mask] + e.ids[:keep]
        return options

    def _encode(self, message, criteria, history):
        max_len, head_max_len = self.cfg["max_len"], self.cfg["head_max_len"]
        options = self._options(criteria, head_max_len)
        instructions = INSTRUCTIONS + (HISTORY_HINT if history else "")
        head = self._tokens(f"choice question: {instructions}").ids[: max(8, head_max_len - sum(map(len, options)))]
        ids, markers = [self.cls, *head, self.sep], []
        for o in options:
            markers.append(len(ids))
            ids += o
        ids.append(self.sep)
        state = {"message": message, **({"history": list(history)} if history else {})}
        room = max(0, max_len - len(ids) - 1)
        ids = (ids + self._tokens(json.dumps(state, ensure_ascii=False)).ids[:room] + [self.sep])[:max_len]
        if any(m >= max_len for m in markers):
            raise ValueError("too many paths for 512 tokens; keep the shortlist on")
        return ids, markers

    def _temperature(self, n):
        b = "2" if n <= 2 else "3-5" if n <= 5 else "6-10" if n <= 10 else "11+"
        return min(5.0, max(0.5, float(self.temps.get(f"choice:{b}", self.cfg["temperature"][0]))))

    def route(self, message, paths, history=None, threshold=None):
        """paths: {path_id: [example phrasings or a description, ...]}. Returns the match (or None) and every probability."""
        none_key = NONE
        while none_key in paths:
            none_key += "_"
        kept = self.shortlist.top(message, paths, self.k) if self.k and len(paths) > self.k else paths
        criteria = {p: " | ".join(f'"{t}"' for t in texts) for p, texts in kept.items()}
        criteria[none_key] = NO_MATCH_DESCRIPTION
        ids, markers = self._encode(message, criteria, history)
        logits = self.sess.run(["logits"], {
            "input_ids": np.array([ids], dtype=np.int64), "attention_mask": np.ones((1, len(ids)), dtype=np.int64),
            "marker_pos": np.array([markers], dtype=np.int64), "marker_mask": np.ones((1, len(markers)), dtype=bool),
            "qtype": np.zeros(1, dtype=np.int64)})[0][0]
        z = logits / self._temperature(len(criteria))
        p = np.exp(z - z.max())
        p /= p.sum()
        got = dict(zip(criteria, p.tolist()))
        probs = {k: got.get(k, 0.0) for k in paths} | {NONE: got[none_key]}
        best = max(paths, key=probs.get)
        ok = probs[best] > probs[NONE] and probs[best] >= (self.threshold if threshold is None else threshold)
        return {"match": best if ok else None, "score": probs[best], "probabilities": probs}


if __name__ == "__main__":
    import sys

    here = os.path.dirname(os.path.abspath(__file__))
    r = Router(here) if os.path.exists(os.path.join(here, "laya.onnx")) else Router.from_pretrained()
    paths = {
        "order_status": ["Customer wants to know the status or location of their order"],
        "cancel_order": ["Customer wants to cancel an existing order"],
        "return_order": ["Customer wants to return an order"],
        "wrong_item": ["Customer received an item different from what they ordered"],
    }
    for msg in sys.argv[1:] or ["where is my parcel #A-7721", "qwewqeqw", "i got blue shoes but ordered black"]:
        out = r.route(msg, paths)
        print(f"{msg!r:45} -> {out['match']} ({out['score']:.2f})")
