# Laya intent router: zero-shot intent classification on CPU

A small zero-shot intent detection model with out-of-scope detection. You give it a user message and a list of intents written in plain English, and it tells you which intent the message belongs to, or that it fits none of them.

No training and no labelled data on your side. You write the intents when you call it, and you can change them on every request. It runs on a CPU with `onnxruntime` in about 150 ms (160 ms p95 on 4 threads), no GPU and no torch.

- **Model on Hugging Face:** [vrajnotviraj/laya-intent-router-150m-onnx](https://huggingface.co/vrajnotviraj/laya-intent-router-150m-onnx)
- **This repo:** the 1-file inference code (`router.py`) and the full training pipeline (`training/`)

```
"i want to cancel my order 88213"         -> cancel_order     0.97
"hey where's my parcel, it's been 5 days" -> order_status     0.97
"ordered black shoes, got blue ones lol"  -> wrong_item       0.97
"what's the weather in paris"             -> none             (0.98 none)
"qwewqeqw"                                -> none             (0.98 none)
```

That last line is why I built it. The original [Laya](https://huggingface.co/convaiinnovations/laya) sent `qwewqeqw` to `order_not_received` with 0.73 confidence. This one puts 0.98 on none.

## Quick start

```bash
git clone https://github.com/vrajnotviraj/laya-intent-router
cd laya-intent-router
pip install onnxruntime tokenizers numpy huggingface_hub
python router.py "where is my parcel"      # downloads ~440 MB of weights once
```

In your own code:

```python
from router import Router

r = Router.from_pretrained()

intents = {
    "check_balance":  ["What's my account balance"],
    "transfer_money": ["Send money to someone", "Transfer funds between accounts"],
    "block_card":     ["Block my card", "My card was lost or stolen"],
    "loan_enquiry":   ["Questions about personal or home loans"],
}

r.route("i think someone stole my card", intents)
# {'match': 'block_card', 'score': 0.98, 'probabilities': {..., '__none__': 0.01}}

r.route("ok", intents)
# {'match': None, 'score': 0.0, 'probabilities': {..., '__none__': 0.98}}
```

Each intent is a key plus 1 or more example phrasings or a short description. `match` is `None` when the message fits nothing, or when the best score is under the threshold (0.625 by default; pass `threshold=` to change it).

## What it's good for

- Chatbot and voicebot intent routing, where the list of intents changes per flow or per customer.
- Out-of-scope detection, so you know when to fall back to a human, an LLM or an "I didn't get that".
- A cheap semantic router in front of an LLM, when a full LLM call is too slow or too expensive for the routing step.
- Customer support triage for e-commerce, banking, insurance, telecom and SaaS.

It's built for short English customer messages. It only speaks English, and it isn't meant for classifying long documents.

## Results: 94.9% routing accuracy, 98.6% out-of-scope recall

Tested on 1,636 hand-written messages across 10 routing setups: e-commerce, retail banking, insurance and telecom, plus an adversarial set of near-duplicates, typos, slang and "don't cancel, just tell me where it is" style traps. **Insurance and telecom were never seen in training.**

| | Laya (original, zero-shot) | Laya-large fine-tuned (teacher) | **This model** |
|---|---|---|---|
| Routing accuracy | 0.728 | 0.950 | **0.949** |
| Catches out-of-scope messages | 0.682 | 0.959 | **0.986** |
| Wrongly accepts out-of-scope | 0.318 | 0.041 | **0.014** |
| Big menus (20 to 45 intents) | 0.704 | 0.938 | **0.943** |
| 6 brand new domains | 0.777 | | **0.920** |
| p95 latency, 4 CPU threads | 252 ms | 496 ms | **160 ms** |
| Size on disk | 636 MB | 636 MB | **304 MB** (+134 MB shortlist) |

So you get the big fine-tuned model's accuracy at a third of its latency and half its size. Latency was measured on an Apple M2 Pro, so measure on your own hardware.

For lists longer than 4 intents, a small embedder (`bge-small-en-v1.5`) picks the 4 closest intents first and the router decides between those and "none". That keeps accuracy between 0.89 and 0.98 from 7 up to 148 intents. It's on by default; pass `shortlist_k=0` to turn it off.

## How it was made

1. Fine-tuned Laya-large (ModernBERT-large with a decision head) as a teacher on about 122k routing episodes. They came from 7 public intent datasets (CLINC150, BANKING77, HWU64, SNIPS and 3 Bitext customer-support sets) plus 76 synthetic workflows across 16 domains. About 40% of episodes had the right intent removed, so the model learns to say "none".
2. Rewrote the prompt format to `key: "phrasing 1" | "phrasing 2"`, with leftover token budget handed to intents that need it. That alone was worth about 3 points.
3. Distilled the teacher into [Ettin-150M](https://huggingface.co/jhu-clsp/ettin-encoder-150m), mixing its probabilities 50/50 with the gold label. Checkpoints were picked with a perturbation-based intent score, because plain accuracy kept picking worse routers.
4. Calibrated temperatures per menu size, then exported to ONNX with 8-bit weight quantization.

Everything trained locally on a 32 GB M2 Pro. The code for every step is in [`training/`](training/), with the commands in [`training/README.md`](training/README.md).

## Where it slips

- **Filler on tiny menus.** With only 2 intents like "Hi" and "Bye", words like "ok", "well" and "nice" can land on "Bye". Give short intents a clear description, or raise the threshold for small menus.
- **It only knows what your phrasings say.** "My card was stolen" won't hit a `block_card` intent whose only phrasing is "Block my card". Add 2 or 3 phrasings that match how people actually talk.
- **Indirect requests and heavy typos** are the weakest slices (about 0.83 to 0.86).
- My test messages were written by the same process as the synthetic training data. Real user logs might be harder, so run your own messages through it before trusting the numbers.

## License

Apache-2.0. Built on [convaiinnovations/laya](https://huggingface.co/convaiinnovations/laya) (Apache-2.0), [jhu-clsp/ettin-encoder-150m](https://huggingface.co/jhu-clsp/ettin-encoder-150m) (MIT) and [BAAI/bge-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5) (MIT). No training data is included; `training/public_data.py` downloads the public datasets, each under its own license.
