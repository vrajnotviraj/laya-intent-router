"""MLX backend for laya_intent_router.py: the same model running on the Apple Silicon GPU.

Used by LayaIntentRouter(backend="mlx" or "auto"). Needs `pip install mlx` and the weights in `mlx/`.
Encoder: ModernBERT (Ettin-150M). Pre-norm layers (layer 0 has no attn_norm), bias-free Linear and
LayerNorm, GeGLU MLP with exact GELU, rotate-half RoPE with a theta per layer type, global attention
on every 3rd layer and a |i - j| <= local_attention // 2 window on the rest. Head: 2 norm-first
transformer layers (ReLU), then a scorer on each [MASK] marker. Weights are stored in fp16; the Linear
layers are quantized to 8 bits at load when mlx/config.json asks for it.
"""

import json
import os

import mlx.core as mx
import mlx.nn as nn
import numpy as np


def _mask(attention_mask, window=None, L=None):
    m = None
    if window is not None:
        i = mx.arange(L)
        m = (mx.abs(i[:, None] - i[None, :]) <= window)[None, None]
    if attention_mask is not None:
        pad = attention_mask.astype(mx.bool_)[:, None, None, :]
        m = pad if m is None else m & pad
    return m


class Attention(nn.Module):
    def __init__(self, d, heads, theta):
        super().__init__()
        self.heads, self.theta = heads, theta
        self.Wqkv = nn.Linear(d, 3 * d, bias=False)
        self.Wo = nn.Linear(d, d, bias=False)

    def __call__(self, x, mask):
        B, L, d = x.shape
        q, k, v = self.Wqkv(x).reshape(B, L, 3, self.heads, -1).transpose(2, 0, 3, 1, 4)
        q = mx.fast.rope(q, q.shape[-1], traditional=False, base=self.theta, scale=1.0, offset=0)
        k = mx.fast.rope(k, k.shape[-1], traditional=False, base=self.theta, scale=1.0, offset=0)
        o = mx.fast.scaled_dot_product_attention(q, k, v, scale=q.shape[-1] ** -0.5, mask=mask)
        return self.Wo(o.transpose(0, 2, 1, 3).reshape(B, L, d))


class MLP(nn.Module):
    def __init__(self, d, inter):
        super().__init__()
        self.Wi = nn.Linear(d, 2 * inter, bias=False)
        self.Wo = nn.Linear(inter, d, bias=False)

    def __call__(self, x):
        a, g = mx.split(self.Wi(x), 2, axis=-1)
        return self.Wo(nn.gelu(a) * g)


class EncoderLayer(nn.Module):
    def __init__(self, c, idx):
        super().__init__()
        d, eps = c["hidden_size"], c["norm_eps"]
        self.sliding = c["layer_types"][idx] == "sliding_attention"
        theta = c["rope_parameters"]["sliding_attention" if self.sliding else "full_attention"]["rope_theta"]
        if idx:
            self.attn_norm = nn.LayerNorm(d, eps=eps, bias=False)
        self.attn = Attention(d, c["num_attention_heads"], theta)
        self.mlp_norm = nn.LayerNorm(d, eps=eps, bias=False)
        self.mlp = MLP(d, c["intermediate_size"])

    def __call__(self, x, mask):
        x = x + self.attn(self.attn_norm(x) if "attn_norm" in self else x, mask)
        return x + self.mlp(self.mlp_norm(x))


class Embeddings(nn.Module):
    def __init__(self, c):
        super().__init__()
        self.tok_embeddings = nn.Embedding(c["vocab_size"], c["hidden_size"])
        self.norm = nn.LayerNorm(c["hidden_size"], eps=c["norm_eps"], bias=False)

    def __call__(self, ids):
        return self.norm(self.tok_embeddings(ids))


class ModernBert(nn.Module):
    def __init__(self, c):
        super().__init__()
        self.window = c["local_attention"] // 2
        self.embeddings = Embeddings(c)
        self.layers = [EncoderLayer(c, i) for i in range(c["num_hidden_layers"])]
        self.final_norm = nn.LayerNorm(c["hidden_size"], eps=c["norm_eps"], bias=False)

    def __call__(self, ids, attention_mask=None):
        x = self.embeddings(ids)
        full, local = _mask(attention_mask), _mask(attention_mask, self.window, ids.shape[1])
        for layer in self.layers:
            x = layer(x, local if layer.sliding else full)
        return self.final_norm(x)


class MultiheadAttention(nn.Module):
    def __init__(self, d, heads):
        super().__init__()
        self.heads = heads
        self.in_proj_weight, self.in_proj_bias = mx.zeros((3 * d, d)), mx.zeros((3 * d,))
        self.out_proj = nn.Linear(d, d)

    def __call__(self, x, mask):
        B, L, d = x.shape
        qkv = x @ self.in_proj_weight.T + self.in_proj_bias
        q, k, v = qkv.reshape(B, L, 3, self.heads, -1).transpose(2, 0, 3, 1, 4)
        o = mx.fast.scaled_dot_product_attention(q, k, v, scale=q.shape[-1] ** -0.5, mask=mask)
        return self.out_proj(o.transpose(0, 2, 1, 3).reshape(B, L, d))


class HeadLayer(nn.Module):
    def __init__(self, d, heads):
        super().__init__()
        self.self_attn = MultiheadAttention(d, heads)
        self.linear1, self.linear2 = nn.Linear(d, 4 * d), nn.Linear(4 * d, d)
        self.norm1, self.norm2 = nn.LayerNorm(d), nn.LayerNorm(d)

    def __call__(self, x, mask):
        x = x + self.self_attn(self.norm1(x), mask)
        return x + self.linear2(nn.relu(self.linear1(self.norm2(x))))


class Head(nn.Module):
    def __init__(self, d, n):
        super().__init__()
        self.layers = [HeadLayer(d, max(1, d // 64)) for _ in range(n)]


class DecisionModel(nn.Module):
    def __init__(self, c):
        super().__init__()
        d = c["hidden_size"]
        self.encoder = ModernBert(c)
        self.head = Head(d, c["head_layers"])
        self.type_emb = nn.Embedding(3, d)
        self.scorer = nn.Sequential(nn.LayerNorm(d), nn.Linear(d, d), nn.GELU(), nn.Linear(d, 1))
        # the act head ships with the weights but routing never reads it
        self.act_head = nn.Sequential(nn.Linear(d + 4, 256), nn.GELU(), nn.Linear(256, c["n_act"]))
        self.temperature = mx.ones((3,))

    def __call__(self, input_ids, attention_mask, marker_pos, marker_mask, qtype):
        h = self.encoder(input_ids, attention_mask) + self.type_emb(qtype)[:, None, :]
        mask = _mask(attention_mask)
        for layer in self.head.layers:
            h = layer(h, mask)
        m = mx.take_along_axis(h, mx.maximum(marker_pos, 0)[:, :, None], axis=1)
        return mx.where(marker_mask, self.scorer(m).squeeze(-1).astype(mx.float32), -1e4)


class Session:
    """Drop-in for the onnxruntime session the router calls: run(["logits"], feeds) -> [np.ndarray]."""

    def __init__(self, weights_dir):
        c = json.load(open(os.path.join(weights_dir, "config.json")))
        self.model = DecisionModel(c)
        self.model.load_weights(os.path.join(weights_dir, "model.safetensors"), strict=True)
        q = c.get("quantization")
        if q:
            nn.quantize(self.model, group_size=q["group_size"], bits=q["bits"],
                        class_predicate=lambda _, m: isinstance(m, nn.Linear) and m.weight.shape[-1] % q["group_size"] == 0)
        self.model.eval()
        mx.eval(self.model.parameters())

    def run(self, names, feeds):
        assert list(names) == ["logits"], names
        am = feeds["attention_mask"]
        f = {k: mx.array(v) for k, v in feeds.items()}
        logits = self.model(f["input_ids"], None if am.all() else f["attention_mask"], f["marker_pos"],
                            f["marker_mask"], f["qtype"])
        return [np.array(logits)]
