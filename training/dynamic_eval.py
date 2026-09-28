"""Dynamic intent-detection testing: fresh seeded perturbations of held-out workflows, scored like production.

  python training/dynamic_eval.py --model models/laya_onnx --name baseline --seed 1
  python training/dynamic_eval.py --model models/teacher_onnx --name teacher_onnx --option_format compact_fill --shortlist_k 4
  python training/dynamic_eval.py --model runs/x/best --dev_intent        # checkpoint-selection draw (training-side dev only)
  python training/dynamic_eval.py --selftest                              # generator invariants, no model

Every question goes through training/evaluate.py (`load_model`, `ask`, `record`, `group_metrics`):
LayaModel.choose + the router decision at the match threshold, the same option formats and shortlist mode.

Sources. Eval mode: data/eval/*.jsonl (incl. large_nodes) + data/eval/fresh/*.jsonl, never training text.
--dev_intent: the source workflow records of data/episodes/dev.jsonl (held out from train by workflow_id),
never data/eval; fixed seed, probes 1,3,4,5,7.

Probes (each: routing acc@t, none_recall@t, false_accept@t, flip vs the unperturbed prediction):
  shuffle       1  path order shuffled
  subset        2  random subset of 2..all paths that keeps the gold path
  gold_removal  3  gold path removed -> must be no_match / below_threshold
  distractors   4  1..10 paths from workflows of other domains added at random positions
  message       5  typo swap/drop/insert, lower, UPPER, punctuation stripped, greeting prefix, polite / angry
                   suffix, entity swap, neutral context sentence
  phrasing      6  1 phrasing per path, reordered phrasings, description-only, example-only
  gibberish     7  keyboard mash, repeated chars, emoji only, numbers only, off-topic sentences
  history       8  1-2 unrelated turns prepended (small talk or another domain's message)
  fresh            the unperturbed fresh workflows (domains absent from training and the static suite)
`clean` (unperturbed held-out questions) is reported for reference and is the flip baseline; it is not in
the score. INTENT SCORE = mean over probes of acc@t (equal weight).
"""

import argparse
import collections
import glob
import json
import os
import random
import re
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import evaluate as ev  # noqa: E402
from common import NONE  # noqa: E402

ROOT = ev.ROOT
EMBEDDER = os.path.join(ROOT, "models", "embed", "bge-small")
DEV_SEED = 20260927
PROBES = ["shuffle", "subset", "gold_removal", "distractors", "message", "phrasing", "gibberish", "history", "fresh"]
DEV_PROBES = ["shuffle", "gold_removal", "distractors", "message", "gibberish"]
# questions per probe at --scale 1 (message: per variant)
SIZES = {"eval": {"pool_eval": 700, "pool_large": 150, "shuffle": 400, "subset": 400, "gold_removal": 400,
                  "distractors": 400, "message": 40, "phrasing": 100, "gibberish": 80, "history": 400},
         "dev": {"pool": 500, "shuffle": 300, "gold_removal": 400, "distractors": 400, "message": 36, "gibberish": 60}}
# paths that legitimately own greetings / filler (same rule as build_episodes.FILLER_CLASH)
FILLER_CLASH = re.compile(r"greet|goodbye|thank|bye|hello|yes|no$|maybe|confirm")
DESC = re.compile(r"^(the )?(customer|client|member|homeowner|user|passenger|patient|guest|caller|subscriber|"
                  r"employee|student|tenant|rider|driver|shopper|traveller|buyer|seller)s?\b", re.I)

KEYROWS = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
NEIGH = {c: (r[max(0, i - 1)] + r[i + 1: i + 2]).replace(c, "") or c for r in KEYROWS for i, c in enumerate(r)}
EMOJI = ["😀", "😂", "👍", "🙏", "🔥", "🎉", "😅", "🤔", "🌟", "🍕", "🚀", "😎", "🙈", "✨", "🥳", "👀"]
PREFIX = ["hi, ", "hello team, ", "pls help ", "hey there, ", "good morning, ", "hi there! "]
POLITE = [" please", ", thank you", ", thanks so much!", ", would really appreciate it", ", thanks in advance"]
ANGRY = [", this is ridiculous!!", ". I'm so fed up.", ", sort it out NOW", ". worst service ever", "!!! seriously"]
CONTEXT = ["I've been a customer for a few years now.", "Sorry, I'm typing this on my phone.",
           "Hope you're having a good day.", "My name is Jordan.", "Quick question for you.",
           "I'm on my lunch break so I'll be brief.", "A friend recommended you to me.", "First time using this chat."]
SMALLTALK = ["hi", "hello", "hey there", "good morning", "are you a bot?", "one sec", "ok", "hmm let me think"]
NAMES = ["Ahmed", "Bella", "Max", "Luna", "Rocky", "Charlie", "Teddy", "Mike", "Jake", "Priya", "Sam", "Sarah",
         "John", "Maria", "Omar", "Fatima", "Chen", "Lucas", "Emma", "Noah", "Olivia", "Ravi", "Aisha", "Tom"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
OFFTOPIC = ["what's the tallest mountain in south america", "how do volcanoes form", "tell me a fact about penguins",
            "what rhymes with orange", "how long do elephants live", "what's the chemical symbol for gold",
            "who wrote the odyssey", "how many strings does a violin have", "why is the sky blue",
            "what's a good stretch for a stiff neck", "how do I fold a fitted sheet", "what is the speed of sound",
            "name a famous jazz musician", "how do you say thank you in japanese", "what's the smallest country",
            "how do magnets work", "what's the best way to cook rice", "who discovered penicillin",
            "how many players are on a rugby team", "what does a koala eat", "what's the plural of cactus",
            "how old is the universe", "what's the hottest planet", "how do I whistle with my fingers",
            "describe a sunset in three words", "what colour do you get mixing blue and yellow",
            "is a whale a mammal", "what's the longest word in english", "how are rainbows made",
            "who built the pyramids", "what is a haiku", "how many keys on a piano", "what do pandas eat",
            "how do I get better at chess", "what's the deepest lake", "why do cats purr",
            "how does a compass work", "what's an easy card trick", "what is the largest desert",
            "who composed the four seasons"]
OFFTOPIC_OPEN = ["", "", "hey, ", "random question: ", "just curious, ", "btw "]


# ---------------------------------------------------------------- sources

def read(path):
    return [json.loads(line) for line in open(path) if line.strip()]


def eval_workflows():
    """Held-out eval + fresh workflow records, each tagged src eval|large|fresh."""
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "eval", "*.jsonl"))):
        for w in read(f):
            out.append({**w, "src": "large" if f.endswith("large_nodes.jsonl") else "eval"})
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "eval", "fresh", "*.jsonl"))):
        out += [{**w, "src": "fresh"} for w in read(f)]
    return out


def dev_workflows():
    """Source workflow records of data/episodes/dev.jsonl (training-side files; the ids are held out of train)."""
    ids = {json.loads(line).get("workflow_id") for line in open(os.path.join(ROOT, "data", "episodes", "dev.jsonl"))}
    files = sorted(glob.glob(os.path.join(ROOT, "data", "synthetic", "*.jsonl"))) + sorted(
        f for f in glob.glob(os.path.join(ROOT, "data", "public", "*.jsonl")) if not f.endswith("_test.jsonl"))
    out = {}
    for f in files:
        for w in read(f):
            if w["workflow_id"] in ids and len(w["paths"]) >= 2 and w["messages"]:
                out[w["workflow_id"]] = {**w, "src": "dev"}
    return [out[k] for k in sorted(out)]


# ---------------------------------------------------------------- perturbations (each returns None when nothing changes)

def _word_edit(text, rng, kind):
    spans = [m.span() for m in re.finditer(r"[A-Za-z]{4,}", text)]
    if not spans:
        return None
    s, e = rng.choice(spans)
    w = text[s:e]
    i = rng.randrange(1, len(w) - 1)
    if kind == "swap":
        if w[i] == w[i + 1]:
            return None
        w = w[:i] + w[i + 1] + w[i] + w[i + 2:]
    elif kind == "drop":
        w = w[:i] + w[i + 1:]
    else:
        w = w[:i] + rng.choice(NEIGH.get(w[i].lower(), "e")) + w[i:]
    return text[:s] + w + text[e:]


def _entity_swap(text, rng):
    def num(m):
        d = m.group()
        return str(rng.randint(1, 9)) + "".join(str(rng.randint(0, 9)) for _ in d[1:]) if len(d) > 1 else str(rng.randint(1, 9))

    def word(pool):
        def f(m):
            new = rng.choice([x for x in pool if x.lower() != m.group().lower()])
            return new.lower() if m.group().islower() else new
        return f

    out = re.sub(r"\d+", num, text)
    for pool in (MONTHS, DAYS):
        out = re.sub(r"\b(" + "|".join(pool) + r")\b", word(pool), out, flags=re.I)
    out = re.sub(r"\b(" + "|".join(NAMES) + r")\b", word(NAMES), out)  # names: capitalised only
    return out


def message_variants(text, rng, in_scope):
    """name -> perturbed text. Label-changing risks (prefix/suffix/context) only for in-scope messages."""
    nopunct = " ".join(re.sub(r"[^\w\s]", " ", text).split())
    v = {"typo_swap": _word_edit(text, rng, "swap"), "typo_drop": _word_edit(text, rng, "drop"),
         "typo_insert": _word_edit(text, rng, "insert"), "lower": text.lower(), "upper": text.upper(),
         "no_punct": nopunct if nopunct else None}
    if in_scope:
        v.update({"prefix": rng.choice(PREFIX) + text, "suffix_polite": text + rng.choice(POLITE),
                  "suffix_angry": text + rng.choice(ANGRY), "entity_swap": _entity_swap(text, rng),
                  "context": rng.choice(CONTEXT) + " " + text})
    return {k: t for k, t in v.items() if t and t != text}


MESSAGE_VARIANTS = ["typo_swap", "typo_drop", "typo_insert", "lower", "upper", "no_punct", "prefix",
                    "suffix_polite", "suffix_angry", "entity_swap", "context"]


def phrasing_variant(paths, rng, kind):
    """Paths with phrasings changed; None if no path changes. A path with no phrasing of the kept style keeps its own."""
    out = []
    for p in paths:
        t = list(p["text"])
        if kind == "one_phrasing":
            t = [rng.choice(t)]
        elif kind == "reorder":
            rng.shuffle(t)
        else:
            keep = [x for x in t if bool(DESC.match(x)) == (kind == "description_only")]
            t = keep or t
        out.append({"path_id": p["path_id"], "text": t})
    return out if any(a["text"] != b["text"] for a, b in zip(out, paths)) else None


def gibberish(rng, kind):
    if kind == "mash":
        row = rng.choice(KEYROWS)
        return "".join(rng.choice(row[max(0, i - 2): i + 3]) for i in [rng.randrange(len(row))] * rng.randint(4, 14))
    if kind == "repeat":
        unit = rng.choice(list("abcdefghijklmnopqrstuvwxyz?!.") + ["ha", "lo", "xo", "ab"])
        return unit * rng.randint(4 if len(unit) == 1 else 3, 12 if len(unit) == 1 else 6)
    if kind == "emoji":
        return "".join(rng.choice(EMOJI) for _ in range(rng.randint(1, 5)))
    if kind == "numbers":
        groups = [str(rng.randint(10 ** (n - 1), 10 ** n - 1)) for n in [rng.randint(1, 6)] * rng.randint(1, 3)]
        return " ".join(groups)
    return rng.choice(OFFTOPIC_OPEN) + rng.choice(OFFTOPIC)


GIBBERISH = ["mash", "repeat", "emoji", "numbers", "off_topic"]


# ---------------------------------------------------------------- the draw

class Screen:
    """bge-small similarity screen that keeps injected text from changing the gold label.
    Note: embedding heuristic, not a human label; thresholds hand-set on bge-small."""

    def __init__(self, embedder_dir=EMBEDDER, threads=4):
        from shortlist import Embedder, Shortlister
        self.sl = Shortlister(Embedder(embedder_dir, threads=threads))

    def sims(self, message, paths):
        return self.sl.scores(message, paths) if paths else np.zeros(0)

    def index(self, paths):
        """Embed a fixed candidate path list once; path_sims(message) then scores all of it (max over phrasings + id)."""
        from shortlist import humanise
        texts, owner = [], []
        for j, p in enumerate(paths):
            for t in list(p["text"]) + [humanise(p["path_id"])]:
                texts.append(t)
                owner.append(j)
        self.V, self.owner, self.n = self.sl.emb.embed(texts), np.array(owner), len(paths)

    def path_sims(self, message):
        out = np.full(self.n, -1.0, dtype=np.float32)
        np.maximum.at(out, self.owner, self.V @ self.sl.emb.embed([message])[0])
        return out


def item(probe, variant, w, paths, message, gold, history=None, base=None, tags=()):
    return {"probe": probe, "variant": variant, "workflow_id": w["workflow_id"], "src": w["src"],
            "domain": w.get("domain"), "paths": paths, "message": message, "history": history, "gold": gold,
            "base": base, "tags": list(tags)}


def build(mode, seed, scale=1.0, probes=None, screen=None):
    """-> (questions, info). questions[i]["base"] points at the index of the unperturbed question (flip rate)."""
    probes = probes or (DEV_PROBES if mode == "dev" else PROBES)
    size = {k: max(1, int(round(v * scale))) for k, v in SIZES[mode].items()}
    wfs = dev_workflows() if mode == "dev" else eval_workflows()
    rng = random.Random(f"{mode}:{seed}:pool")
    msgs = lambda w: [(w, m) for m in w["messages"]]
    if mode == "dev":
        pool = []
        for _ in range(size["pool"]):
            w = rng.choice(wfs)
            pool.append((w, rng.choice(w["messages"])))
    else:
        ev_msgs = [x for w in wfs if w["src"] == "eval" for x in msgs(w)]
        lg_msgs = [x for w in wfs if w["src"] == "large" for x in msgs(w)]
        pool = rng.sample(ev_msgs, min(size["pool_eval"], len(ev_msgs))) + rng.sample(lg_msgs, min(size["pool_large"], len(lg_msgs)))
        pool += [x for w in wfs if w["src"] == "fresh" for x in msgs(w)]  # every fresh question
    qs = [item("fresh" if w["src"] == "fresh" else "clean", "-", w, w["paths"], m["text"], m["gold"], m.get("history"),
               tags=m.get("tags", ())) for w, m in pool]
    for i, q in enumerate(qs):
        q["base"] = i
    if "fresh" not in probes:
        for q in qs:
            q["probe"] = "clean"
    base_ix = list(range(len(qs)))
    small = [i for i in base_ix if qs[i]["src"] != "large"]  # nodes a probe may add to / take subsets of
    ins = lambda ix: [i for i in ix if qs[i]["gold"] != NONE]
    nones = lambda ix: [i for i in ix if qs[i]["gold"] == NONE]
    by_wf = {w["workflow_id"]: w for w in wfs}
    info = {"mode": mode, "seed": seed, "scale": scale, "workflows": len(wfs), "pool": len(qs), "screened": collections.Counter()}

    def pick(r, ix, n, none_share=0.25):
        a, b = ins(ix), nones(ix)
        nb = min(len(b), int(round(n * none_share)))
        return [r.choice(a) for _ in range(n - nb)] + [r.choice(b) for _ in range(nb)] if a else []

    def base_of(i):
        return qs[i], by_wf[qs[i]["workflow_id"]]

    new = []
    if "shuffle" in probes:
        r = random.Random(f"{mode}:{seed}:shuffle")
        for i in pick(r, [i for i in base_ix if len(qs[i]["paths"]) > 1], size["shuffle"]):
            q, w = base_of(i)
            paths = list(q["paths"])
            while paths == q["paths"]:
                r.shuffle(paths)
            new.append(item("shuffle", f"{len(paths)} paths", w, paths, q["message"], q["gold"], q["history"], i, q["tags"]))
    if "subset" in probes:
        r = random.Random(f"{mode}:{seed}:subset")
        for i in pick(r, [i for i in small if len(qs[i]["paths"]) > 2], size["subset"]):
            q, w = base_of(i)
            n = r.randint(2, len(q["paths"]))
            keep = {q["gold"]} if q["gold"] != NONE else set()
            others = [p["path_id"] for p in q["paths"] if p["path_id"] not in keep]
            keep |= set(r.sample(others, n - len(keep)))
            paths = [p for p in q["paths"] if p["path_id"] in keep]
            bucket = "all" if n == len(q["paths"]) else "2 paths" if n == 2 else "3-4 paths" if n <= 4 else "5+ paths"
            new.append(item("subset", bucket, w, paths, q["message"],
                            q["gold"], q["history"], i, q["tags"]))
    if "gold_removal" in probes:
        r = random.Random(f"{mode}:{seed}:gold_removal")
        for i in pick(r, [i for i in base_ix if len(qs[i]["paths"]) >= 3], size["gold_removal"], none_share=0):
            q, w = base_of(i)
            paths = [p for p in q["paths"] if p["path_id"] != q["gold"]]
            new.append(item("gold_removal", q["src"], w, paths, q["message"], NONE, q["history"], i, q["tags"]))
    if "distractors" in probes:
        r = random.Random(f"{mode}:{seed}:distractors")
        screen = screen or Screen()
        uniq = {}  # (path_id, phrasings) -> [path, domains it appears in]
        for x in wfs:
            if x["src"] != "large":
                for p in x["paths"]:
                    uniq.setdefault((p["path_id"], tuple(p["text"])), [p, set()])[1].add(x.get("domain"))
        cand = list(uniq.values())
        cand = r.sample(cand, min(1500, len(cand)))  # note: capped candidate pool keeps the dev draw's embedding pass short
        screen.index([p for p, _ in cand])
        for i in pick(r, small, size["distractors"]):
            q, w = base_of(i)
            s = screen.path_sims(q["message"])
            gold_s = screen.sims(q["message"], [p for p in q["paths"] if p["path_id"] == q["gold"]])
            limit = 0.75 if q["gold"] == NONE else min(0.80, float(gold_s[0]) - 0.02)
            taken = {x["path_id"] for x in q["paths"]}
            pool_d = [(p, s[j]) for j, (p, doms) in enumerate(cand) if w.get("domain") not in doms and p["path_id"] not in taken]
            ok = [p for p, sim in pool_d if sim < limit]
            info["screened"]["distractors"] += len(pool_d) - len(ok)
            n = r.randint(1, 10)
            seen, add = set(), []
            for p in r.sample(ok, len(ok)):
                if p["path_id"] not in seen:
                    seen.add(p["path_id"])
                    add.append(p)
                if len(add) == n:
                    break
            paths = list(q["paths"])
            for p in add:
                paths.insert(r.randint(0, len(paths)), p)
            new.append(item("distractors", "+1-3" if n <= 3 else "+4-6" if n <= 6 else "+7-10", w, paths, q["message"],
                            q["gold"], q["history"], i, q["tags"]))
    if "message" in probes:
        r = random.Random(f"{mode}:{seed}:message")
        for v in MESSAGE_VARIANTS:
            got, tries = 0, 0
            cands = small
            while got < size["message"] and tries < 200 * size["message"]:
                tries += 1
                i = r.choice(cands)
                q, w = base_of(i)
                gold_path = q["gold"] if q["gold"] != NONE else ""
                in_scope = q["gold"] != NONE and not FILLER_CLASH.search(gold_path)
                if q["gold"] != NONE and not in_scope and v in ("prefix", "suffix_polite", "suffix_angry", "entity_swap", "context"):
                    continue
                if q["gold"] == NONE and v not in ("typo_swap", "typo_drop", "typo_insert", "lower", "upper", "no_punct"):
                    continue
                if q["gold"] == NONE and r.random() > 0.25:  # keep ~20% none
                    continue
                t = message_variants(q["message"], r, in_scope).get(v)
                if t is None:
                    continue
                new.append(item("message", v, w, q["paths"], t, q["gold"], q["history"], i, q["tags"]))
                got += 1
    if "phrasing" in probes:
        r = random.Random(f"{mode}:{seed}:phrasing")
        for v in ["one_phrasing", "reorder", "description_only", "example_only"]:
            got, tries = 0, 0
            while got < size["phrasing"] and tries < 200 * size["phrasing"]:
                tries += 1
                i = r.choice(small)
                q, w = base_of(i)
                if q["gold"] == NONE and r.random() > 0.33:
                    continue
                paths = phrasing_variant(q["paths"], r, v)
                if paths is None:
                    continue
                new.append(item("phrasing", v, w, paths, q["message"], q["gold"], q["history"], i, q["tags"]))
                got += 1
    if "gibberish" in probes:
        r = random.Random(f"{mode}:{seed}:gibberish")
        screen = screen or Screen()
        homes = sorted({qs[i]["workflow_id"] for i in small})
        for v in GIBBERISH:
            got, tries = 0, 0
            while got < size["gibberish"] and tries < 50 * size["gibberish"]:
                tries += 1
                w = by_wf[r.choice(homes)]
                t = gibberish(r, v)
                if v == "off_topic" and len(s := screen.sims(t, w["paths"])) and s.max() >= 0.75:
                    info["screened"]["off_topic"] += 1
                    continue
                if v == "repeat" and any(FILLER_CLASH.search(p["path_id"]) for p in w["paths"]):
                    continue  # "hahaha" / "lololo" could belong to a greeting/thanks path
                new.append(item("gibberish", v, w, w["paths"], t, NONE, None, None, ["gibberish" if v != "off_topic" else "off_topic"]))
                got += 1
    if "history" in probes:
        r = random.Random(f"{mode}:{seed}:history")
        other = collections.defaultdict(list)  # domain -> in-scope texts of other domains
        doms = {w.get("domain") for w in wfs}
        foreign = [(w.get("domain"), m["text"]) for w in wfs if w["src"] != "large" for m in w["messages"] if m["gold"] != NONE]
        for d in doms:
            other[d] = [t for dd, t in foreign if dd != d]
        for i in pick(r, [i for i in small if not qs[i]["history"]], size["history"]):
            q, w = base_of(i)
            if q["gold"] != NONE and FILLER_CLASH.search(q["gold"]):
                continue
            n = r.randint(1, 2)
            kind = r.choice(["smalltalk", "other_domain", "mixed"])
            hist = [r.choice(SMALLTALK) if kind == "smalltalk" or (kind == "mixed" and j == 0) else r.choice(other[w.get("domain")])
                    for j in range(n)]
            new.append(item("history", f"{kind}", w, q["paths"], q["message"], q["gold"], hist, i, q["tags"]))
    qs += new
    info["screened"] = dict(info["screened"])
    info["n_questions"] = len(qs)
    return qs, info


# ---------------------------------------------------------------- scoring

def outcome(p, thr):
    return p["choice"] if p["dec"][thr] == "matched" else NONE


def run(model, qs, thr, shortlister=None, k=0, log_every=0):
    """Score every question through evaluate.ask/record. ValueError (node does not fit the chooser) -> skipped."""
    preds, t0 = [None] * len(qs), time.time()
    for n, q in enumerate(qs):
        try:
            ans, intents, none_key, ms = ev.ask(model, q["paths"], q["message"], q["history"], shortlister, k)
        except ValueError:
            continue
        preds[n] = {**q, **ev.record(ans, intents, none_key, ms, q["gold"], model, [thr])}
        if log_every and (n + 1) % log_every == 0:
            print(f"  {n + 1}/{len(qs)} questions, {time.time() - t0:.0f}s", file=sys.stderr, flush=True)
    return preds


def summarize(preds, thr, probes):
    ok = [p for p in preds if p]
    for n, p in enumerate(preds):
        if p:
            b = preds[p["base"]] if p["base"] is not None else None
            p["flip"] = (None if p["probe"] in ("gold_removal", "gibberish") or b is None or p["base"] == n
                         else outcome(p, thr) != outcome(b, thr))
    by = collections.defaultdict(list)
    for p in ok:
        by[p["probe"]].append(p)

    def block(ps):
        m = ev.group_metrics(ps, thr)
        fl = [p["flip"] for p in ps if p["flip"] is not None]
        m["flip_rate"] = round(float(np.mean(fl)), 4) if fl else None
        for src in ("eval", "large", "fresh", "dev"):
            sel = [p for p in ps if p["src"] == src]
            if sel and len({p["src"] for p in ps}) > 1:
                m[f"acc@{thr}_{src}"] = ev.group_metrics(sel, thr)[f"acc@{thr}"]
        return m

    table = {name: block(by[name]) for name in ["clean"] + probes if by.get(name)}
    variants = {name: {v: block([p for p in by[name] if p["variant"] == v]) for v in sorted({p["variant"] for p in by[name]})}
                for name in probes if by.get(name) and name != "fresh"}
    accs = {name: table[name][f"acc@{thr}"] for name in probes if name in table}
    worst = min(accs, key=accs.get) if accs else None
    return {"intent_score": round(float(np.mean(list(accs.values()))), 4) if accs else None,
            "worst_probe": worst, "worst_acc": accs.get(worst), "probes": table, "variants": variants,
            "skipped": sum(p is None for p in preds),
            "latency_ms": {"p50": ev.pct([p["ms"] for p in ok], 50), "p95": ev.pct([p["ms"] for p in ok], 95)}}


def to_md(r):
    t = r["threshold"]
    cols = ["probe", "n", "n_none", f"acc@{t}", f"path_acc@{t}", f"none_recall@{t}", f"false_accept@{t}", "flip_rate",
            f"acc@{t}_eval", f"acc@{t}_fresh", f"acc@{t}_large", "ece"]
    md = [f"# Dynamic intent eval: {r['name']}", "",
          f"Model `{r['model']}`, backend {r['backend']}, option_format {r['option_format']}, head_max_len {r['head_max_len']}, "
          f"shortlist k={r['shortlist_k'] or 'off'}. Mode {r['info']['mode']}, seed {r['info']['seed']}, scale {r['info']['scale']}: "
          f"{r['info']['n_questions']} questions from {r['info']['workflows']} workflows ({r['summary']['skipped']} skipped: node does not fit the chooser). "
          f"Threshold {t} (production decision logic). Wall clock {r['wall_s'] / 60:.1f} min. Built by `training/dynamic_eval.py`.", "",
          f"**INTENT SCORE {r['summary']['intent_score']:.4f}** (mean acc@{t} over {len(r['probe_names'])} probes, equal weight). "
          f"Worst probe: **{r['summary']['worst_probe']}** ({r['summary']['worst_acc']:.4f}).", "",
          "`flip_rate`: share of perturbed questions whose routed outcome (matched path, or none) differs from the same "
          "message's unperturbed prediction. Not defined for gold_removal (the gold changes) or gibberish (no base). "
          "`clean` = unperturbed held-out questions, the flip baseline, not in the score.", "",
          "## Probes", "", ev.table([{"probe": k, **v} for k, v in r["summary"]["probes"].items()], cols), "",
          "## Variants", ""]
    for name, vs in r["summary"]["variants"].items():
        md += [f"### {name}", "", ev.table([{"probe": k, **v} for k, v in vs.items()],
                                           ["probe", "n", "n_none", f"acc@{t}", f"none_recall@{t}", f"false_accept@{t}", "flip_rate"]), ""]
    lat = r["summary"]["latency_ms"]
    md += ["## Notes", "", f"Latency over all questions: p50 {lat['p50']} ms, p95 {lat['p95']} ms. "
           f"Similarity-screened candidates (label protection): {r['info']['screened']}.", ""]
    return "\n".join(md)


# ---------------------------------------------------------------- dev-intent (checkpoint selection)

_DEV_CACHE = {}


def dev_intent(model, shortlist_k=4, embedder=EMBEDDER, threads=4, thr=None, seed=DEV_SEED, scale=1.0):
    """Fixed-seed dynamic draw from dev workflows (probes 1,3,4,5,7) -> (intent score, summary). The draw and the
    embedder are built once per process, so every checkpoint sees identical questions."""
    thr = thr or ev.PROD_THRESHOLD
    key = (seed, scale, embedder, threads)
    if key not in _DEV_CACHE:
        screen = Screen(embedder, threads)
        from shortlist import Shortlister
        qs, info = build("dev", seed, scale, DEV_PROBES, screen)
        _DEV_CACHE[key] = (qs, info, Shortlister(screen.sl.emb))
    qs, info, sl = _DEV_CACHE[key]
    preds = run(model, qs, thr, sl if shortlist_k else None, shortlist_k)
    s = summarize(preds, thr, DEV_PROBES)
    return s["intent_score"], s


def live_model(net, cfg, tokenizer_json, device):
    """An in-memory torch net (e.g. mid-training) as a production-logic chooser. Puts net in eval(); caller restores train()."""
    m = ev.TorchLaya(None, device, net=net, cfg=cfg, tokenizer_json=tokenizer_json)
    ev.set_format(m, m.option_format)
    return m


# ---------------------------------------------------------------- main

def selftest():
    qs, info = build("eval", 1, scale=0.1)
    qs2, _ = build("eval", 1, scale=0.1)
    qs3, _ = build("eval", 2, scale=0.1)
    strip = lambda q: json.dumps({k: v for k, v in q.items()}, sort_keys=True, ensure_ascii=False)
    assert list(map(strip, qs)) == list(map(strip, qs2)), "same seed must give the same draw"
    assert list(map(strip, qs)) != list(map(strip, qs3)), "different seeds must differ"
    for q in qs:
        ids = [p["path_id"] for p in q["paths"]]
        assert len(ids) == len(set(ids)), q
        if q["probe"] == "gold_removal":
            assert q["gold"] == NONE and qs[q["base"]]["gold"] not in ids
        elif q["gold"] != NONE:
            assert q["gold"] in ids, q
        if q["probe"] == "shuffle":
            assert ids != [p["path_id"] for p in qs[q["base"]]["paths"]] and sorted(ids) == sorted(p["path_id"] for p in qs[q["base"]]["paths"])
        if q["probe"] == "distractors":
            assert {p["path_id"] for p in qs[q["base"]]["paths"]} <= set(ids)
    assert {q["probe"] for q in qs} == set(PROBES) | {"clean"}, {q["probe"] for q in qs}
    dev, dinfo = build("dev", DEV_SEED, scale=0.1)
    ev_text = {m["text"] for w in eval_workflows() for m in w["messages"]}
    assert not any(q["src"] != "dev" for q in dev) and not any(q["message"] in ev_text and q["probe"] != "gibberish" for q in dev)
    assert {q["probe"] for q in dev} == set(DEV_PROBES) | {"clean"}
    r = random.Random(0)
    assert _entity_swap("order 4471 on Monday for Bella", r) != "order 4471 on Monday for Bella"
    assert phrasing_variant([{"path_id": "a", "text": ["Customer wants x", "do x"]}], r, "example_only")[0]["text"] == ["do x"]
    print(f"selftest ok: eval draw {info['n_questions']} q at scale 0.1, dev draw {dinfo['n_questions']} q")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model")
    ap.add_argument("--name")
    ap.add_argument("--seed", type=int, default=1, help="draw seed (different seeds = different draws); --dev_intent uses DEV_SEED")
    ap.add_argument("--dev_intent", action="store_true", help="fixed-seed dev-workflow draw (probes 1,3,4,5,7) for checkpoint selection")
    ap.add_argument("--scale", type=float, default=1.0, help="multiply every probe size (smoke runs)")
    ap.add_argument("--probes", default=None, help="comma list (default: all for the mode)")
    ap.add_argument("--shortlist_k", type=int, default=0)
    ap.add_argument("--embedder", default=EMBEDDER)
    ap.add_argument("--shortlist_agg", choices=["max", "top2"], default="max")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--device", default=None)
    ap.add_argument("--threshold", type=float, default=ev.PROD_THRESHOLD)
    ap.add_argument("--option_format", choices=list(ev.OPTION_FORMATS), default=None)
    ap.add_argument("--head_max_len", type=int, default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.model:
        ap.error("--model is required")
    thr, mode = a.threshold, "dev" if a.dev_intent else "eval"
    name = a.name or ("dev_intent" if a.dev_intent else "unnamed")
    probes = a.probes.split(",") if a.probes else (DEV_PROBES if a.dev_intent else PROBES)
    t0 = time.time()
    model, backend, size = ev.load_model(a.model, a.threads, a.device, a.option_format, a.head_max_len)
    screen = Screen(a.embedder, a.threads)
    from shortlist import Shortlister
    sl = Shortlister(screen.sl.emb, agg=a.shortlist_agg) if a.shortlist_k else None
    qs, info = build(mode, DEV_SEED if a.dev_intent else a.seed, a.scale, probes, screen)
    print(f"{mode} draw: {info['n_questions']} questions, {info['workflows']} workflows, built in {time.time() - t0:.0f}s", file=sys.stderr)
    preds = run(model, qs, thr, sl, a.shortlist_k, log_every=250)
    s = summarize(preds, thr, probes)
    report = {"name": name, "model": os.path.abspath(a.model), "backend": backend, "size_bytes": size,
              "option_format": model.option_format, "head_max_len": model.head_max_len, "shortlist_k": a.shortlist_k,
              "threshold": thr, "probe_names": probes, "info": info, "summary": s, "wall_s": round(time.time() - t0, 1),
              "argv": sys.argv[1:]}
    base = os.path.join(ROOT, "reports", f"dyn_{name}")
    json.dump(report, open(base + ".json", "w"), indent=1)
    with open(base + ".preds.jsonl", "w") as f:
        for p in preds:
            if p:
                f.write(json.dumps({k: p[k] for k in ("probe", "variant", "src", "workflow_id", "message", "history", "gold",
                                                      "choice", "confidence", "dec", "flip", "base")}
                                   | {"paths": [x["path_id"] for x in p["paths"]]}, ensure_ascii=False) + "\n")
    open(base + ".md", "w").write(to_md(report))
    print(to_md(report))


if __name__ == "__main__":
    main()
