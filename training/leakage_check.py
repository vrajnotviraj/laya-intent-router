"""Leakage audit: held-out eval (data/eval) vs training data (data/synthetic, data/public minus *_test).

Flags, for every training message and path phrasing:
  exact       identical to an eval message/phrasing (after strip)
  normalized  identical after lowercase + drop punctuation/digits + collapse spaces
  char5       char 5-gram Jaccard >= 0.8 on the normalized form
  token       token-set Jaccard >= 0.8 (both sides >= 3 tokens)
  heldout     insurance / telecom keywords (workflow domain/id, path, phrasing or message)
  arabic      Arabic script anywhere (also scanned in eval and *_test, report only)

  python training/leakage_check.py          # audit only, exit 1 if leaks
  python training/leakage_check.py --fix    # delete offending TRAINING items, re-check until clean,
                                                  # write reports/leakage.md
  python training/leakage_check.py --episodes F.jsonl ...   # audit derived episode files (message,
                                                  # history, phrasings); with --fix, drop flagged episodes
Fix rules: drop a flagged message; drop a flagged phrasing; a path left with no phrasings (or flagged
heldout) is dropped with its messages; a workflow left with < 2 paths or 0 messages is dropped.
Eval files are never modified.
"""

import glob
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = 0.8
ARABIC = re.compile(r"[؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿]")
HELDOUT = re.compile(
    r"insur|telecom|telco|roaming|sim ?card|\besim\b|broadband|postpaid|prepaid (plan|mobile|sim|balance)"
    r"|mobile (carrier|network|operator|data)|data (plan|pack|bundle)|deductible|policyholder|underwrit"
    r"|airtime|talk ?time|phone bill|(recharge|top ?up) my (phone|mobile|number)|port(ing)? my number",
    re.I,
)


def norm(s):
    return " ".join(re.sub(r"[^\w\s]|[\d_]", " ", s.lower()).split())


def char5(n):
    p = f" {n} "
    return frozenset(p[i:i + 5] for i in range(max(1, len(p) - 4)))


def toks(n):
    t = frozenset(n.split())
    return t if len(t) >= 3 else None


def jac(a, b):
    return len(a & b) / len(a | b)


class Index:
    """Jaccard >= T search with prefix filtering (exact, no false negatives)."""

    def __init__(self, sets):
        self.sets = sets
        self.df = Counter(g for s in sets for g in s)
        self.post = defaultdict(list)
        for i, s in enumerate(sets):
            for g in self.prefix(s):
                self.post[g].append(i)

    def prefix(self, s):
        k = len(s) - math.ceil(T * len(s)) + 1
        return sorted(s, key=lambda g: (self.df.get(g, 0), g))[:k]

    def query(self, s):
        cands = {i for g in self.prefix(s) for i in self.post.get(g, ())}
        return [i for i in cands if jac(s, self.sets[i]) >= T]


def load(path):
    return [json.loads(line) for line in open(path)]


def eval_texts():
    out = []  # (text, where)
    for f in sorted(glob.glob(str(ROOT / "data/eval/**/*.jsonl"), recursive=True)):  # includes data/eval/fresh/
        for r in load(f):
            for p in r["paths"]:
                out += [(t, f"{Path(f).name}:{r['workflow_id']}:phrasing") for t in p["text"]]
            out += [(m["text"], f"{Path(f).name}:{r['workflow_id']}:message") for m in r["messages"]]
    return out


def train_files():
    pub = [f for f in glob.glob(str(ROOT / "data/public/*.jsonl")) if not f.endswith("_test.jsonl")]
    return sorted(glob.glob(str(ROOT / "data/synthetic/*.jsonl"))) + sorted(pub)


class Checker:
    def __init__(self):
        ev = eval_texts()
        self.exact = {t.strip(): w for t, w in ev}
        self.norm = {norm(t): (t, w) for t, w in ev if norm(t)}
        keys = list(self.norm)
        self.keys = keys
        self.c5 = Index([char5(k) for k in keys])
        tk = [(k, toks(k)) for k in keys]
        tk = [(k, s) for k, s in tk if s]
        self.tkeys = [k for k, _ in tk]
        self.tok = Index([s for _, s in tk])
        self.cache = {}

    def leak(self, text):
        """-> (reason, eval_text, eval_where) or None."""
        if ARABIC.search(text):
            return ("arabic", "", "")
        if HELDOUT.search(text):
            return ("heldout", "", "")
        s = text.strip()
        if s in self.exact:
            return ("exact", s, self.exact[s])
        n = norm(text)
        if not n:
            return None
        if n not in self.cache:
            hit = None
            if n in self.norm:
                hit = ("normalized", *self.norm[n])
            else:
                c = self.c5.query(char5(n))
                if c:
                    hit = ("char5", *self.norm[self.keys[c[0]]])
                else:
                    ts = toks(n)
                    c = self.tok.query(ts) if ts else []
                    if c:
                        hit = ("token", *self.norm[self.tkeys[c[0]]])
            self.cache[n] = hit
        return self.cache[n]


def audit_file(path, ck, fix=False):
    """Returns (findings, removed Counter, new records)."""
    findings, removed, keep = [], Counter(), []
    for r in load(path):
        wf_hit = HELDOUT.search(f"{r['domain']} {r['workflow_id']}")
        if wf_hit:
            findings.append(("heldout", "workflow", r["workflow_id"], "", ""))
            removed["workflows"] += 1
            removed["messages"] += len(r["messages"])
            continue
        paths, dropped_paths = [], set()
        for p in r["paths"]:
            if HELDOUT.search(p["path_id"]) or ARABIC.search(p["path_id"]):
                findings.append(("heldout", "path_id", f"{r['workflow_id']}:{p['path_id']}", "", ""))
                dropped_paths.add(p["path_id"])
                removed["paths"] += 1
                continue
            texts = []
            for t in p["text"]:
                h = ck.leak(t)
                if h:
                    findings.append((h[0], "phrasing", t, h[1], h[2]))
                    removed["phrasings"] += 1
                else:
                    texts.append(t)
            if texts:
                paths.append({**p, "text": texts})
            else:
                dropped_paths.add(p["path_id"])
                removed["paths"] += 1
        msgs = []
        for m in r["messages"]:
            if m["gold"] in dropped_paths:
                removed["messages"] += 1
                continue
            h = ck.leak(m["text"])
            if h:
                findings.append((h[0], "message", m["text"], h[1], h[2]))
                removed["messages"] += 1
            else:
                msgs.append(m)
        if len(paths) < 2 or not msgs:
            removed["workflows"] += 1
            removed["messages"] += len(msgs)
            continue
        keep.append({**r, "paths": paths, "messages": msgs})
    if fix:
        with open(path, "w") as f:
            f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in keep)
    return findings, removed, keep


def arabic_anywhere():
    return {Path(f).relative_to(ROOT).as_posix(): n for f in glob.glob(str(ROOT / "data/**/*.jsonl"), recursive=True)
            if (n := sum(bool(ARABIC.search(line)) for line in open(f, encoding="utf-8")))}


def run(fix):
    ck = Checker()
    per_file, total = {}, Counter()
    for f in train_files():
        findings, removed, _ = audit_file(f, ck, fix)
        per_file[Path(f).relative_to(ROOT).as_posix()] = (findings, removed)
        total.update(Counter(x[0] for x in findings))
    return per_file, total


def selftest():
    import tempfile
    global ROOT
    real = ROOT
    with tempfile.TemporaryDirectory() as d:
        ROOT = Path(d)
        (ROOT / "data/eval").mkdir(parents=True)
        (ROOT / "data/synthetic").mkdir(parents=True)
        (ROOT / "data/public").mkdir(parents=True)
        wf = lambda wid, paths, msgs: {"workflow_id": wid, "domain": "x", "source": "t", "paths": [
            {"path_id": k, "text": v} for k, v in paths.items()], "messages": [{"text": t, "gold": g, "tags": []} for t, g in msgs]}
        (ROOT / "data/eval/e.jsonl").write_text(json.dumps(wf("e", {"a": ["Cancel my order please"]},
            [("where is my parcel number 12345 right now", "a"), ("block the card that I lost yesterday", "a")])) + "\n")
        (ROOT / "data/synthetic/s.jsonl").write_text(json.dumps(wf("s", {"a": ["cancel my order, please!"], "b": ["hi", "yo"]}, [
            ("Where is my parcel number 999 right now?", "b"),   # normalized
            ("block the card that i lost yesterda", "b"),        # char5
            ("I want to file an insurance claim", "b"),          # heldout
            ("مرحبا", "b"),                              # arabic
            ("totally unrelated sentence here", "b"),            # kept
            ("cancel it", "a"),                                  # path a loses its only phrasing -> dropped
        ])) + "\n")
        (ROOT / "data/public/p_test.jsonl").write_text("")
        per_file, total = run(fix=True)
        assert total == Counter(normalized=2, char5=1, heldout=1, arabic=1), total
        out = load(ROOT / "data/synthetic/s.jsonl")
        assert out == [], out  # only path b left -> < 2 paths -> workflow dropped
        _, total = run(fix=False)
        assert not total
    ROOT = real
    print("selftest ok")


def report(rounds, after_total):
    lines = ["# Leakage audit", "",
             "Built by `training/leakage_check.py --fix`. Eval data (`data/eval/`) vs training data "
             "(`data/synthetic/*.jsonl`, `data/public/*.jsonl` without `*_test`). Eval files were not changed.", "",
             "Checks on every training message and path phrasing, against every eval message and eval phrasing: "
             "exact match, normalized match (lowercase, punctuation and digits stripped), char 5-gram Jaccard >= 0.8, "
             "token-set Jaccard >= 0.8 (3+ tokens), insurance/telecom keywords (workflow domain/id, path id, "
             "phrasing, message), Arabic script.", ""]
    for i, (per_file, total, removed) in enumerate(rounds, 1):
        lines += [f"## Round {i}", "", "| check | hits |", "|---|---|"]
        lines += [f"| {k} | {v} |" for k, v in sorted(total.items())] or ["| none | 0 |"]
        lines += ["", "Removed from training:", "", "| file | messages | phrasings | paths | workflows |", "|---|---|---|---|---|"]
        for f, (_, r) in per_file.items():
            if r:
                lines.append(f"| {f} | {r['messages']} | {r['phrasings']} | {r['paths']} | {r['workflows']} |")
        lines.append(f"| **total** | {removed['messages']} | {removed['phrasings']} | {removed['paths']} | {removed['workflows']} |")
        lines.append("")
        if i == 1:
            lines += ["Examples (first 40 non-exact hits):", "", "| check | kind | training text | eval text | eval source |", "|---|---|---|---|---|"]
            ex = [x for fnd, _ in per_file.values() for x in fnd if x[0] != "exact"][:40]
            cell = lambda s: s.replace("|", "\\|")
            lines += [f"| {a} | {b} | {cell(c)} | {cell(d)} | {e} |" for a, b, c, d, e in ex]
            lines.append("")
    ar = arabic_anywhere()
    lines += ["## Final state", "",
              f"Re-run after fixes: {sum(after_total.values())} hits ({'clean' if not after_total else dict(after_total)}).",
              f"Arabic script lines anywhere under `data/` (eval, test and training): {ar or 'none'}.", "",
              "Note: the fix edits the JSONL outputs only. Re-running `training/public_data.py` or a synth builder "
              "brings the leaked rows back, so run `training/leakage_check.py --fix` after any rebuild.", ""]
    (ROOT / "reports/leakage.md").write_text("\n".join(lines))


def audit_episodes(files, fix):
    """Episode files ({paths, message, history}) derived from training data: flag every text like audit_file."""
    ck, bad, memo = Checker(), 0, {}
    for f in files:
        eps = load(f)
        hits = Counter()
        keep = []
        for e in eps:
            texts = [e["message"]] + list(e.get("history") or []) + [t for p in e["paths"] for t in p["text"]]
            why = [r for t in texts if (r := memo[t] if t in memo else memo.setdefault(t, ck.leak(t)))]
            hits.update(r[0] for r in why)
            if not why:
                keep.append(e)
        bad += len(eps) - len(keep)
        print(f"{f}: {len(eps)} episodes, {len(eps) - len(keep)} with a flagged text, hits {dict(hits)}")
        if fix and len(keep) < len(eps):
            with open(f, "w") as fh:
                fh.writelines(json.dumps(e, ensure_ascii=False) + "\n" for e in keep)
    sys.exit(1 if bad and not fix else 0)


def main():
    if "--selftest" in sys.argv:
        return selftest()
    fix = "--fix" in sys.argv
    if "--episodes" in sys.argv:
        return audit_episodes([x for x in sys.argv[sys.argv.index("--episodes") + 1:] if not x.startswith("--")], fix)
    rounds = []
    while True:
        per_file, total = run(fix)
        removed = sum((r for _, r in per_file.values()), Counter())
        print(f"round {len(rounds) + 1}: hits {dict(total)} removed {dict(removed) if fix else '-'}")
        if not fix or not total:
            break
        rounds.append((per_file, total, removed))
    if fix:
        report(rounds, total)
        print("wrote reports/leakage.md")
    ar = arabic_anywhere()
    if ar:
        print("arabic lines:", ar)
    sys.exit(1 if (total or ar) else 0)


if __name__ == "__main__":
    main()
