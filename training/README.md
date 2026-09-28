# Training code

This folder has the code that trained the intent router. The router gets a customer message and a list of paths, each with a few example phrasings. It picks one path, or `__none__` when no path fits.

We fine-tuned the Laya decision model ([convaiinnovations/laya](https://huggingface.co/convaiinnovations/laya), ModernBERT-large with a DecisionModel head) as a teacher. Then we distilled it into an Ettin-150M student (`jhu-clsp/ettin-encoder-150m`) and exported the student as an 8-bit ONNX model. The routing is zero-shot: paths arrive with each request, so nothing here is tied to a fixed label set.

## What each script does

| Script | What it does |
|---|---|
| `common.py` | Builds the model input for one episode (prompt, options, `[MASK]` markers). Formats: `prod` (the original Laya prompt format), `compact` (`key: "p1" \| "p2"`) and `compact_fill` (compact, plus leftover option budget is shared out). `python training/common.py` runs its self-checks. |
| `public_data.py` | Downloads the public intent datasets and turns them into workflow records in `data/public/`. |
| `synth_0.py`, `synth_2.py`, `synth3/synth_3_a.py`, `synth3/synth_3_b.py` | Hand-written synthetic workflows (retail, food delivery, travel, hotels, clinics, SaaS helpdesk) written to `data/synthetic/`. All brand names in them are made up. |
| `build_episodes.py` | Turns workflow records into training episodes (`data/episodes/train.jsonl`, `dev.jsonl`): random path subsets, shuffled order, gold path removal, some history. |
| `leakage_check.py` | Checks training data against the held-out eval set (exact, normalised and fuzzy matches, held-out domains). `--fix` deletes leaking training items. |
| `train.py` | Four modes: `teacher` (fine-tune Laya), `label` (teacher soft labels for every episode), `student` (distill into Ettin), `calibrate` (refit temperatures per option-count bucket). |
| `export_onnx.py` | Exports a checkpoint to `laya.onnx` + `tokenizer.json` + `rl_agent_config.json`, with 8-bit MatMulNBits quantization by default. `--check N` compares torch and ONNX logits. |
| `evaluate.py` | Static eval on `data/eval/*.jsonl` with the router decision logic (match, no match, below threshold). Writes `reports/<name>.md`, `.json` and `.preds.jsonl`. Works with ONNX dirs and torch checkpoints. |
| `dynamic_eval.py` | Seeded perturbation probes (shuffled paths, removed gold path, distractor paths, noisy messages, gibberish and so on) and the intent score used to pick checkpoints. |
| `shortlist.py` | Embedding shortlist for nodes with many paths: only the top k paths go to the router. |

## Layout

Run everything from the repo root, one level above this folder. The scripts read and write `data/`, `models/`, `runs/` and `reports/` there. None of these are in the repo.

Workflow records (one JSON object per line) look like this:

```json
{"workflow_id": "shop_1", "domain": "ecommerce", "paths": [{"path_id": "cancel_order", "text": ["cancel my order"]}],
 "messages": [{"text": "pls cancel #1234", "gold": "cancel_order", "tags": ["entity"]}]}
```

`data/eval/` holds your held-out eval workflows in the same format. It is never used for training. `data/eval/large_nodes.jsonl` (nodes with many paths) is only scored when you pass it with `--eval`. `data/eval/fresh/` holds workflows from domains absent from training, for `dynamic_eval.py`.

The shortlist embedder dir (default `models/embed/bge-small`) needs `model.onnx`, `tokenizer.json` and `shortlist_config.json` (we used `{"pooling": "cls", "max_len": 128}` with an ONNX export of bge-small).

## Pipeline

1. `public_data.py`
2. the synth scripts
3. `build_episodes.py`
4. `leakage_check.py --fix`
5. `train.py --mode teacher`
6. `train.py --mode label` (soft labels)
7. `train.py --mode student`
8. `train.py --mode calibrate`
9. `export_onnx.py`
10. `evaluate.py` and `dynamic_eval.py`

## Example commands

```sh
pip install -r training/requirements.txt

# data
python training/public_data.py
python training/synth_0.py && python training/synth_2.py
python training/synth3/synth_3_a.py && python training/synth3/synth_3_b.py
python training/build_episodes.py --n 100000 --seed 7
python training/leakage_check.py --fix

# teacher: fine-tune Laya (ModernBERT-large)
python training/train.py --mode teacher --init convaiinnovations/laya \
  --train data/episodes/train.jsonl --dev data/episodes/dev.jsonl --out runs/teacher \
  --epochs 1 --micro_batch 16 --grad_accum 4 --max_tokens 8192 \
  --option_format compact_fill --head_max_len 384 --eval_every 100 --dev_max 2000

# soft labels from the teacher
python training/train.py --mode label --init runs/teacher/best \
  --train data/episodes/train.jsonl --out data/episodes/train_distill.jsonl

# student: distill into Ettin-150M, pick checkpoints by the dev intent score
python training/train.py --mode student --encoder jhu-clsp/ettin-encoder-150m \
  --train data/episodes/train.jsonl --distill_file data/episodes/train_distill.jsonl \
  --dev data/episodes/dev.jsonl --option_format compact_fill --head_max_len 384 --alpha 0.5 \
  --micro_batch 16 --max_tokens 4096 --grad_accum 6 --epochs 2 --eval_every 250 \
  --select_metric intent --select_every 500 --select_shortlist_k 4 --out runs/student

# refit temperatures, export, evaluate
python training/train.py --mode calibrate --init runs/student/best --dev data/episodes/dev.jsonl
python training/export_onnx.py runs/student/best models/student_onnx --quant nbits8 --check 5
OMP_NUM_THREADS=4 python training/evaluate.py --model models/student_onnx --name student --shortlist_k 4 --threads 4
OMP_NUM_THREADS=4 python training/dynamic_eval.py --model models/student_onnx --name student --shortlist_k 4 --seed 1
```

A crashed run can continue from `last/` with `--resume`. Without `--calib`, `train.py` holds out a slice of `--train` for the temperature refit.

## Hardware

We trained on an Apple M2 Pro with 32 GB of memory, using MPS in fp32 (bf16 was slower on that chip). Latency numbers come from onnxruntime on 4 CPU threads.

## Data and licences

`public_data.py` downloads the datasets. They are not included in this repo.

- Bitext customer support, retail e-commerce and retail banking: CDLA-Sharing-1.0
- CLINC150: CC BY 3.0
- BANKING77 and HWU64: CC BY 4.0
- SNIPS: CC0

## The laya package

`train.py` imports the `laya` package for the model builder and calibration helpers. `requirements.txt` installs it from GitHub, pinned to the commit we used. The ONNX eval path (`evaluate.py`, `dynamic_eval.py` with an ONNX model dir) only needs onnxruntime, tokenizers and numpy.
