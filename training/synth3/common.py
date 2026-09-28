"""Parse hand-authored workflow text blocks into WORKFLOW RECORD FORMAT JSONL.

Block syntax:
  @wf <workflow_id>
  #path <path_id>      then "= phrasing" lines and "- message || tag,tag" lines
  #none                then "- message || tag,tag" lines (gold "__none__")
"""
import json
import re

TAGS = {"t": "typo", "s": "slang", "e": "entity", "m": "multi_sentence", "n": "near_duplicate",
        "g": "gibberish", "o": "off_topic", "x": "missing_intent", "sh": "short", "p": "polite",
        "a": "angry", "q": "question", "i": "indirect"}
BANNED = ["customer wants to know the status or location of their order", "customer wants to cancel an existing order",
          "block my card", "what's my balance", "insurance", "arabic", "telecom", "sim card", "carrier"]
NONE_TAGS = {"gibberish", "off_topic", "missing_intent"}


def parse(block, domain, source):
    wf, path = None, None
    for raw in block.strip().splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("@wf "):
            wf = {"workflow_id": line[4:].strip(), "domain": domain, "source": source, "paths": [], "messages": []}
        elif line.startswith("#path "):
            path = {"path_id": line[6:].strip(), "text": []}
            wf["paths"].append(path)
        elif line == "#none":
            path = None
        elif line.startswith("= "):
            path["text"].append(line[2:].strip())
        elif line.startswith("- "):
            text, _, tags = line[2:].rpartition("||")
            assert text, f"missing tags: {line}"
            wf["messages"].append({"text": text.strip(), "gold": path["path_id"] if path else "__none__",
                                   "tags": [TAGS[t.strip()] for t in tags.split(",")]})
        else:
            raise ValueError(f"bad line: {line}")
    return wf


def validate(wf):
    ids = [p["path_id"] for p in wf["paths"]]
    assert 3 <= len(ids) <= 12 and len(set(ids)) == len(ids), wf["workflow_id"]
    for p in wf["paths"]:
        assert 1 <= len(p["text"]) <= 8, p["path_id"]
    seen = set()
    for m in wf["messages"]:
        key = re.sub(r"\s+", " ", m["text"].lower())
        assert key not in seen, f"dup in {wf['workflow_id']}: {m['text']}"
        seen.add(key)
        assert m["tags"]
    blob = json.dumps(wf).lower()
    for b in BANNED:
        assert b not in blob, f"banned '{b}' in {wf['workflow_id']}"
    counts = {g: sum(m["gold"] == g for m in wf["messages"]) for g in ids + ["__none__"]}
    assert min(counts.values()) >= 20, (wf["workflow_id"], counts)
    return counts


def write(blocks, domain, source, out):
    wfs = [parse(b, domain, source) for b in blocks]
    ids = [w["workflow_id"] for w in wfs]
    assert len(set(ids)) == len(ids)
    with open(out, "w") as f:
        for w in wfs:
            c = validate(w)
            print(w["workflow_id"], len(w["paths"]), "paths", len(w["messages"]), "msgs", c)
            f.write(json.dumps(w, ensure_ascii=False) + "\n")
    print(out, len(wfs), "workflows", sum(len(w["messages"]) for w in wfs), "messages")
