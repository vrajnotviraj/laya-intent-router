"""Synthetic training workflows: e-commerce retail (synth_0_a) and food delivery/grocery (synth_0_b).

Hand-written per workflow: paths with phrasings + messages as 'text|tag,tag' lines.
Run: python training/synth_0.py [--check N]   (prints N random labels for eyeballing)
"""
import json, random, re, sys
from pathlib import Path

from synth_0_data_a import WORKFLOWS as A
from synth_0_data_b import WORKFLOWS as B

OUT = Path(__file__).resolve().parent.parent / "data" / "synthetic"
TAGS = {"typo", "slang", "entity", "multi_sentence", "near_duplicate", "gibberish", "off_topic",
        "missing_intent", "short", "polite", "angry", "question", "indirect"}
FORBIDDEN = ["status or location of their order", "cancel an existing order", "block my card",
             "what's my balance", "insurance", "claim", "telecom", "sim card", "recharge", "data plan"]
ARABIC = re.compile(r"[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]")


def parse(block):
    out = []
    for line in block.strip().splitlines():
        t, _, tags = line.strip().rpartition("|")
        out.append((t.strip(), [x.strip() for x in tags.split(",") if x.strip()]))
    return out


def build(wf, domain):
    paths = [{"path_id": k, "text": v} for k, v in wf["paths"].items()]
    msgs = []
    for gold, block in wf["msgs"].items():
        assert gold == "__none__" or gold in wf["paths"], (wf["id"], gold)
        for text, tags in parse(block):
            assert text and tags and set(tags) <= TAGS, (wf["id"], text, tags)
            msgs.append({"text": text, "gold": gold, "tags": tags})
    texts = [m["text"].lower() for m in msgs]
    dup = {t for t in texts if texts.count(t) > 1}
    assert not dup, (wf["id"], dup)
    blob = json.dumps(paths + msgs).lower()
    for f in FORBIDDEN:
        assert f not in blob, (wf["id"], f)
    assert not ARABIC.search(blob), wf["id"]
    assert 3 <= len(paths) <= 12, wf["id"]
    for p in wf["paths"]:
        assert set(wf["msgs"]) >= {p, "__none__"}, (wf["id"], p)
    return {"workflow_id": wf["id"], "domain": domain, "source": "synth_0_handwritten",
            "paths": paths, "messages": msgs}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    allrecs = []
    for fname, domain, wfs in [("synth_0_a.jsonl", "ecommerce_retail", A),
                               ("synth_0_b.jsonl", "food_delivery_grocery", B)]:
        recs = [build(w, domain) for w in wfs]
        with open(OUT / fname, "w") as f:
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        for r in recs:
            n = {}
            for m in r["messages"]:
                n[m["gold"]] = n.get(m["gold"], 0) + 1
            print(f"{fname} {r['workflow_id']}: {len(r['paths'])} paths, {len(r['messages'])} msgs, "
                  f"min/path {min(v for k, v in n.items() if k != '__none__')}, none {n['__none__']}")
        allrecs += recs
    if "--check" in sys.argv:
        k = int(sys.argv[sys.argv.index("--check") + 1])
        pool = [(r["workflow_id"], m) for r in allrecs for m in r["messages"]]
        for wid, m in random.Random(0).sample(pool, k):
            print(f"{wid:24} {m['gold']:24} {m['text']}")


if __name__ == "__main__":
    main()
