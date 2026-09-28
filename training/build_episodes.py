"""Workflow records (data/synthetic, data/public non-test) -> train.py episodes.

  python training/build_episodes.py [--n 100000] [--seed 7]

Writes data/episodes/{train,dev}.jsonl and data/episodes/stats.json. Dev = ~5% of training
workflows held out by md5(workflow_id); data/eval and data/public/*_test are never read for text
(eval messages are only loaded to keep generated gibberish from colliding with them).

Mix: 50% synthetic, 40% public, 10% extra __none__ (gibberish, filler, off-topic on foreign paths).
Per episode: random path subset (2-15), shuffled order, 1..all phrasings per path, gold-drop
(gold path removed -> relabelled __none__, never for near_duplicate messages), occasional history.
"""

import argparse
import collections
import glob
import hashlib
import json
import os
import random
import re
import string

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NONE = "__none__"
MAX_PATHS = 15
FILLER = ["ok", "okay", "k", "kk", "hmm", "hmmm", "umm", "uh", "lol", "haha", "yes", "no", "hello", "hi", "hey",
          "thanks", "thank you", "ty", "cool", "fine", "sure", "alright", "test", "testing", "?", "??", "...", "."]
FILLER_CLASH = re.compile(r"greet|goodbye|thank|bye|hello|yes|no$|maybe|confirm")  # paths that legitimately own filler
KEYROWS = ["qwertyuiop", "asdfghjkl", "zxcvbnm", "1234567890"]
EMOJI = ["😀", "😂", "👍", "🙏", "🔥", "❤️", "😡", "🤔", "🎉", "💯"]
STOP = set("what when where which with would could should there their about from have this that your you are "
           "the and for can how does just into they them then than been will want need like make".split())


def read(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def is_dev(workflow_id):
    return int(hashlib.md5(workflow_id.encode()).hexdigest(), 16) % 20 == 0


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def gibberish(rng):
    kind = rng.randrange(8)
    if kind == 0:  # keyboard mash along a row
        row = rng.choice(KEYROWS[:3])
        s = "".join(rng.choice(row[max(0, i - 2):i + 3]) for i in [rng.randrange(len(row))] * rng.randint(4, 12))
    elif kind == 1:  # random letters, maybe spaced
        s = " ".join("".join(rng.choices(string.ascii_lowercase, k=rng.randint(2, 8))) for _ in range(rng.randint(1, 3)))
    elif kind == 2:  # repeated chars
        s = rng.choice(string.ascii_lowercase + "?!.") * rng.randint(3, 12)
    elif kind == 3:  # digits
        s = "".join(rng.choices(string.digits, k=rng.randint(1, 10)))
    elif kind == 4:  # emoji only
        s = "".join(rng.choices(EMOJI, k=rng.randint(1, 4)))
    elif kind == 5:  # repeated syllable
        s = ("".join(rng.choices(string.ascii_lowercase, k=rng.randint(2, 3)))) * rng.randint(2, 5)
    elif kind == 6:  # mixed junk
        s = "".join(rng.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=rng.randint(4, 14)))
    else:  # row slice
        row = rng.choice(KEYROWS)
        i = rng.randrange(len(row) - 3)
        s = row[i:i + rng.randint(3, len(row) - i)]
    return s.upper() if rng.random() < 0.1 else s


def content_words(t):
    return {w for w in norm(t).split() if len(w) >= 4 and w not in STOP}


def sample_paths(rng, paths, keep_id, drop_id=None):
    """Random subset of 2..15 paths (keep_id always kept, drop_id never), shuffled, phrasings subsampled."""
    pool = [p for p in paths if p["path_id"] not in (keep_id, drop_id)]
    rng.shuffle(pool)
    n_max = min(MAX_PATHS, len(pool) + (keep_id is not None))
    k = n_max if rng.random() < 0.3 else rng.randint(2, n_max)
    chosen = pool[:k - (keep_id is not None)] + [p for p in paths if p["path_id"] == keep_id]
    rng.shuffle(chosen)
    out = []
    for p in chosen:
        text = list(p["text"])
        if rng.random() < 0.6:
            text = rng.sample(text, rng.randint(1, len(text)))
        out.append({"path_id": p["path_id"], "text": text})
    return out


def make_episode(rng, wf, msg, p_drop, p_hist):
    gold, tags = msg["gold"], list(msg["tags"])
    ids = {p["path_id"] for p in wf["paths"]}
    assert gold == NONE or gold in ids, (wf["workflow_id"], gold)
    aug = []
    drop = (gold != NONE and len(wf["paths"]) >= 3 and "near_duplicate" not in tags and rng.random() < p_drop)
    if drop:
        paths = sample_paths(rng, wf["paths"], None, drop_id=gold)
        gold, tags, aug = NONE, tags + ["missing_intent"], ["gold_drop"]
    else:
        paths = sample_paths(rng, wf["paths"], None if gold == NONE else gold)
    history = None
    if gold != NONE and rng.random() < p_hist:
        others = [m["text"] for m in wf["messages"] if m["gold"] != NONE and m["text"] != msg["text"]]
        if others:
            history = rng.sample(others, min(len(others), rng.randint(1, 2)))
            aug.append("history")
    kept = {p["path_id"] for p in paths}
    assert 2 <= len(paths) <= MAX_PATHS
    assert (msg["gold"] not in kept) if drop else (gold == NONE or gold in kept)
    return {"paths": paths, "message": msg["text"], "history": history, "gold": gold,
            "source": wf["source"], "domain": wf["domain"], "workflow_id": wf["workflow_id"], "tags": tags, "aug": aug}


def extra_none(rng, synth, all_wfs, offtopic, eval_norm):
    """A __none__ message on foreign paths: gibberish on any workflow, filler/off-topic on synthetic ones."""
    kind = rng.choices(["gibberish", "filler", "off_topic"], [0.5, 0.15, 0.35])[0]
    for _ in range(50):
        if kind == "gibberish":
            text, wf = gibberish(rng), rng.choice(all_wfs)
            if norm(text) in eval_norm:
                continue
        elif kind == "filler":
            text, wf = rng.choice(FILLER), rng.choice(synth)
            if any(FILLER_CLASH.search(p["path_id"]) for p in wf["paths"]):
                continue
        else:
            (text, src_domain), wf = rng.choice(offtopic), rng.choice(synth)
            if wf["domain"] == src_domain:
                continue
        paths = sample_paths(rng, wf["paths"], None)
        if kind == "off_topic":  # note: lexical guard only; a paraphrase-level clash can still slip through
            if content_words(text) & set().union(*(content_words(t + " " + p["path_id"].replace("_", " "))
                                                   for p in paths for t in p["text"])):
                continue
        tags = [kind if kind != "filler" else "off_topic"] + (["short"] if len(text.split()) <= 3 else [])
        return {"paths": paths, "message": text, "history": None, "gold": NONE, "source": "extra_none",
                "domain": wf["domain"], "workflow_id": wf["workflow_id"], "tags": tags, "aug": ["extra_none"]}
    raise RuntimeError(f"could not place a {kind} message")


def build(rng, synth, public, n, p_drop, p_hist, eval_norm):
    all_wfs = synth + public
    offtopic = [(m["text"], wf["domain"]) for wf in all_wfs for m in wf["messages"]
                if m["gold"] == NONE and "off_topic" in m["tags"] and "missing_intent" not in m["tags"]]
    pools = {name: [(wf, m) for wf in wfs for m in wf["messages"]] for name, wfs in (("synthetic", synth), ("public", public))}
    quota = {"synthetic": round(n * 0.5), "public": round(n * 0.4)}
    eps = []
    for name, k in quota.items():
        pool = pools[name]
        picks = rng.sample(pool, k) if k <= len(pool) else [rng.choice(pool) for _ in range(k)]
        eps += [make_episode(rng, wf, m, p_drop, p_hist) for wf, m in picks]
    eps += [extra_none(rng, synth, all_wfs, offtopic, eval_norm) for _ in range(n - len(eps))]
    rng.shuffle(eps)
    return eps


def stats(eps):
    none = [e for e in eps if e["gold"] == NONE]
    hist = collections.Counter(len(e["paths"]) for e in eps)
    return {
        "episodes": len(eps),
        "none_ratio": round(len(none) / len(eps), 4),
        "none_by_origin": dict(collections.Counter(
            "gold_drop" if "gold_drop" in e["aug"] else "extra_none" if "extra_none" in e["aug"] else "original"
            for e in none)),
        "by_source": dict(collections.Counter(e["source"] if e["source"] == "extra_none" else
                                              "public" if e["source"].startswith("public:") else "synthetic" for e in eps)),
        "with_history": sum("history" in e["aug"] for e in eps),
        "path_count_hist": {k: hist[k] for k in sorted(hist)},
        "unique_messages": len({e["message"] for e in eps}),
        "workflows": len({e["workflow_id"] for e in eps}),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100000, help="train episodes (dev gets 5%% of this)")
    ap.add_argument("--p_drop", type=float, default=0.19, help="gold-drop prob per in-scope message (~15%% of all)")
    ap.add_argument("--p_hist", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "episodes"))
    a = ap.parse_args()

    synth = [r for f in sorted(glob.glob(os.path.join(ROOT, "data/synthetic/*.jsonl"))) for r in read(f)]
    public = [r for f in sorted(glob.glob(os.path.join(ROOT, "data/public/*.jsonl"))) if not f.endswith("_test.jsonl")
              for r in read(f)]
    eval_wfs = [r for f in glob.glob(os.path.join(ROOT, "data/eval/*.jsonl")) for r in read(f)]
    eval_norm = {norm(m["text"]) for r in eval_wfs for m in r["messages"]}
    assert not {r["workflow_id"] for r in eval_wfs} & {r["workflow_id"] for r in synth + public}

    os.makedirs(a.out, exist_ok=True)
    out = {}
    for split, n in (("train", a.n), ("dev", max(200, a.n // 20))):
        pick = (lambda r: is_dev(r["workflow_id"]) == (split == "dev"))
        s, p = [r for r in synth if pick(r)], [r for r in public if pick(r)]
        eps = build(random.Random(f"{a.seed}:{split}"), s, p, n, a.p_drop, a.p_hist, eval_norm)
        with open(os.path.join(a.out, f"{split}.jsonl"), "w") as f:
            for i, e in enumerate(eps):
                f.write(json.dumps({"id": f"{split}:{i}", **e}, ensure_ascii=False) + "\n")
        out[split] = {**stats(eps), "source_workflows": {"synthetic": len(s), "public": len(p)}}
    tr = {e["workflow_id"] for e in map(json.loads, open(os.path.join(a.out, "train.jsonl")))}
    dv = {e["workflow_id"] for e in map(json.loads, open(os.path.join(a.out, "dev.jsonl")))}
    assert not tr & dv, "dev workflows leaked into train"
    json.dump(out, open(os.path.join(a.out, "stats.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
