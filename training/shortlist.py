"""Shortlist stage: keep the k paths whose phrasings are closest to the message.

Each phrasing (plus the humanised path_id, "cancel_order" -> "cancel order") is embedded on its own
with a small English ONNX embedder on CPU. A path scores as its best phrasing (agg="max") or the mean
of its best two (agg="top2"). Phrasing vectors are cached per node, keyed by a hash of the paths,
so a node's phrasings are embedded once. Nodes with <= k paths pass through untouched. The chooser
always gets `__none__` on top of the shortlist; that is the caller's job (build_criteria adds it).

  sl = Shortlister(Embedder("models/embed/bge-small"))
  sl.shortlist("where is my parcel", paths, k=6)   # -> paths subset, original order

Model dir: model.onnx + tokenizer.json + shortlist_config.json {"pooling": "cls"|"mean", "prefix": ""}.
`python training/shortlist.py` runs the self-check.
"""

import hashlib
import json
import os
import re
from collections import OrderedDict

import numpy as np

# pooling / prefix per candidate (model cards): bge CLS, the rest mean; e5 wants "query: " on both sides
DEFAULT_CFG = {"minilm": {"pooling": "mean"}, "bge-small": {"pooling": "cls"}, "gte-small": {"pooling": "mean"},
               "e5-small": {"pooling": "mean", "prefix": "query: "}}


def humanise(path_id: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", path_id)
    return re.sub(r"[_\-.:/]+", " ", s).strip().lower()


class Embedder:
    def __init__(self, model_dir, threads=4, max_len=128):
        import onnxruntime as ort
        from tokenizers import Tokenizer

        cfg_path = os.path.join(model_dir, "shortlist_config.json")
        cfg = json.load(open(cfg_path)) if os.path.exists(cfg_path) else DEFAULT_CFG[os.path.basename(model_dir.rstrip("/"))]
        self.pooling, self.prefix = cfg["pooling"], cfg.get("prefix", "")
        self.tok = Tokenizer.from_file(os.path.join(model_dir, "tokenizer.json"))
        self.tok.enable_truncation(max_len)
        self.tok.enable_padding(pad_id=self.tok.token_to_id("[PAD]") or 0)
        o = ort.SessionOptions()
        o.intra_op_num_threads, o.inter_op_num_threads = threads, 1
        self.sess = ort.InferenceSession(os.path.join(model_dir, "model.onnx"), o, providers=["CPUExecutionProvider"])
        self.inputs = {i.name for i in self.sess.get_inputs()}

    def embed(self, texts, batch=64) -> np.ndarray:
        """Unit vectors, one per text."""
        out = []
        for i in range(0, len(texts), batch):
            encs = self.tok.encode_batch([self.prefix + t for t in texts[i: i + batch]])
            ids = np.array([e.ids for e in encs], dtype=np.int64)
            mask = np.array([e.attention_mask for e in encs], dtype=np.int64)
            feed = {"input_ids": ids, "attention_mask": mask, "token_type_ids": np.zeros_like(ids)}
            h = self.sess.run(None, {k: v for k, v in feed.items() if k in self.inputs})[0]
            v = h[:, 0] if self.pooling == "cls" else (h * mask[..., None]).sum(1) / np.maximum(mask.sum(1, keepdims=True), 1)
            out.append(v)
        v = np.concatenate(out).astype(np.float32)
        return v / np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-8)


def node_key(paths) -> str:
    sig = "\n".join(f"{p['path_id']}\t" + "\t".join(sorted(p["text"])) for p in paths)  # path order matters: owner rows index it
    return hashlib.blake2b(sig.encode(), digest_size=16).hexdigest()


class Shortlister:
    def __init__(self, embedder, agg="max", use_id=True, cache_size=512):
        self.emb, self.agg, self.use_id = embedder, agg, use_id
        self.cache, self.cache_size = OrderedDict(), cache_size  # node_key -> (vectors, owner index per row)

    def _node(self, paths):
        key = node_key(paths)
        hit = self.cache.get(key)
        if hit is not None:
            self.cache.move_to_end(key)
            return hit
        texts, owner = [], []
        for j, p in enumerate(paths):
            for t in list(p["text"]) + ([humanise(p["path_id"])] if self.use_id else []):
                texts.append(t)
                owner.append(j)
        hit = (self.emb.embed(texts), np.array(owner))
        self.cache[key] = hit
        if len(self.cache) > self.cache_size:
            self.cache.popitem(last=False)
        return hit

    def scores(self, message, paths) -> np.ndarray:
        """One score per path, in path order."""
        vecs, owner = self._node(paths)
        sims = vecs @ self.emb.embed([message])[0]
        out = np.empty(len(paths), dtype=np.float32)
        for j in range(len(paths)):
            s = np.sort(sims[owner == j])[::-1]
            out[j] = s[0] if self.agg == "max" or len(s) == 1 else s[:2].mean()
        return out

    def shortlist(self, message, paths, k):
        """Top-k paths in their original order; all paths when len(paths) <= k (no embedding at all)."""
        if len(paths) <= k:
            return list(paths)
        s = self.scores(message, paths)
        keep = set(np.argsort(-s, kind="stable")[:k].tolist())
        return [p for j, p in enumerate(paths) if j in keep]


def _check():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sl = Shortlister(Embedder(os.path.join(root, "models", "embed", "bge-small")))
    paths = [{"path_id": "order_status", "text": ["where is my order"]}, {"path_id": "cancel_order", "text": ["cancel my order"]},
             {"path_id": "book_flight", "text": ["book a flight"]}, {"path_id": "weather", "text": ["what's the weather"]}]
    assert humanise("cancelOrder") == "cancel order" and humanise("ins_auto__file_claim") == "ins auto file claim"
    assert sl.shortlist("x", paths, 4) == paths and not sl.cache  # passthrough never embeds
    got = sl.shortlist("please cancel the order I placed", paths, 2)
    assert [p["path_id"] for p in got] == ["order_status", "cancel_order"], got  # original order kept
    assert len(sl.cache) == 1
    sl.shortlist("flight to paris", paths, 2)
    assert len(sl.cache) == 1  # warm: same node reuses its vectors
    rev = paths[::-1]  # same paths, other order: must not reuse the first order's owner rows
    assert [p["path_id"] for p in sl.shortlist("please cancel the order I placed", rev, 2)] == ["cancel_order", "order_status"]
    print("shortlist OK")


if __name__ == "__main__":
    _check()
