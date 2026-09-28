"""Export a Laya-layout checkpoint to an ONNX dir (laya.onnx + tokenizer.json + rl_agent_config.json).

    python training/export_onnx.py CKPT_OR_HUB_ID OUT_DIR [--quant nbits8|dynamic|none] [--check 5]

Interface (same as the original Laya ONNX build): inputs input_ids, attention_mask,
marker_pos, marker_mask, qtype; outputs logits, act_logits. nbits8 = MatMulNBits 8-bit
blocks of 32 (what production ships); dynamic = ORT dynamic int8. Copies tokenizer.json and
rl_agent_config.json beside laya.onnx. --check compares fp32 torch vs fp32 ONNX vs quantized
logits on N prompts built with training/common.py (the checkpoint's prompt format).
"""

import argparse
import os
import shutil
import sys
import tempfile

import numpy as np
import onnx
import onnxruntime as ort
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Encoder, load_tokenizer  # noqa: E402
from train import load_checkpoint  # noqa: E402

NAMES_IN = ["input_ids", "attention_mask", "marker_pos", "marker_mask", "qtype"]


def export(model, path):
    model.eval()
    inputs = (torch.randint(0, 100, (1, 16)), torch.ones((1, 16), dtype=torch.long),
              torch.tensor([[1, 5]]), torch.tensor([[True, True]]), torch.tensor([0]))
    torch.onnx.export(
        model, inputs, path, export_params=True, opset_version=18, do_constant_folding=True,  # default dynamo exporter; dynamo=False bakes seq_len into the head attention
        input_names=NAMES_IN, output_names=["logits", "act_logits"],
        dynamic_axes={"input_ids": {0: "batch_size", 1: "seq_len"}, "attention_mask": {0: "batch_size", 1: "seq_len"},
                      "marker_pos": {0: "batch_size", 1: "num_markers"}, "marker_mask": {0: "batch_size", 1: "num_markers"},
                      "qtype": {0: "batch_size"}, "logits": {0: "batch_size", 1: "num_markers"}, "act_logits": {0: "batch_size"}})


def quantize(fp32_path, out_path, how):
    m = onnx.load(fp32_path)
    del m.graph.value_info[:]  # shapes traced at seq_len=16 contradict the dynamic axes
    if how == "dynamic":
        from onnxruntime.quantization import QuantType, quantize_dynamic
        clean = fp32_path.replace(".onnx", ".clean.onnx")
        onnx.save(m, clean, save_as_external_data=True, location=os.path.basename(clean) + ".data")
        quantize_dynamic(clean, out_path, weight_type=QuantType.QInt8, use_external_data_format=True)
        return
    from onnxruntime.quantization.matmul_nbits_quantizer import DefaultWeightOnlyQuantConfig, MatMulNBitsQuantizer
    q = MatMulNBitsQuantizer(m, algo_config=DefaultWeightOnlyQuantConfig(block_size=32, is_symmetric=True, bits=8, accuracy_level=4))
    q.process()
    q.model.save_model_to_file(out_path, use_external_data_format=True)


def session(path, threads=4):
    o = ort.SessionOptions()
    o.intra_op_num_threads, o.inter_op_num_threads = threads, 1
    return ort.InferenceSession(path, sess_options=o, providers=["CPUExecutionProvider"])


def check(model, enc, paths, n):
    eps = [
        {"paths": [{"path_id": "order_status", "text": ["where is my order", "track package"]},
                   {"path_id": "cancel_order", "text": ["cancel my order", "Customer wants to cancel an order"]}],
         "message": m, "gold": "__none__"}
        for m in ["wheres my parcel #A12", "cancel it now!!", "qwewqeqw", "what is the weather", "i dont want the shoes anymore"]
    ][:n]
    sess = {k: session(p) for k, p in paths.items()}
    worst = {k: 0.0 for k in sess}
    for e in eps:
        it = enc.encode(e)
        feed = {"input_ids": np.array([it["ids"]], np.int64), "attention_mask": np.ones((1, len(it["ids"])), np.int64),
                "marker_pos": np.array([it["markers"]], np.int64), "marker_mask": np.ones((1, len(it["markers"])), bool),
                "qtype": np.array([0], np.int64)}
        with torch.no_grad():
            ref = model(*(torch.from_numpy(feed[k]) for k in NAMES_IN))[0].numpy()[0]
        row = [f"{e['message'][:24]:24s} torch={np.round(ref, 3)}"]
        for k, s in sess.items():
            z = s.run(["logits"], feed)[0][0]
            worst[k] = max(worst[k], float(np.abs(z - ref).max()))
            row.append(f"{k} maxdiff={np.abs(z - ref).max():.4f} argmax_same={z.argmax() == ref.argmax()}")
        print(" | ".join(row))
    print("max |logit diff| vs torch fp32:", worst)
    return worst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ckpt"), ap.add_argument("out")
    ap.add_argument("--quant", choices=["nbits8", "dynamic", "none"], default="nbits8")
    ap.add_argument("--check", type=int, default=0)
    a = ap.parse_args()

    model, cfg, d = load_checkpoint(a.ckpt)
    model.encoder.config.reference_compile = False
    os.makedirs(a.out, exist_ok=True)
    out = os.path.join(a.out, "laya.onnx")
    with tempfile.TemporaryDirectory(dir=a.out) as tmp:
        fp32 = os.path.join(tmp, "laya.onnx")
        export(model, fp32)
        if a.quant == "none":
            onnx.save(onnx.load(fp32), out, save_as_external_data=True, location="laya.onnx.data")
        else:
            quantize(fp32, out, a.quant)
        if a.check:
            enc = Encoder.from_cfg(load_tokenizer(os.path.join(d, "tokenizer", "tokenizer.json")), cfg)
            check(model, enc, {"onnx_fp32": fp32, f"onnx_{a.quant}": out}, a.check)
    shutil.copy(os.path.join(d, "tokenizer", "tokenizer.json"), a.out)
    shutil.copy(os.path.join(d, "rl_agent_config.json"), a.out)
    print(f"wrote {a.out}: {sorted(os.listdir(a.out))}")


if __name__ == "__main__":
    main()
