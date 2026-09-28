"""Turn one routing episode into Laya model inputs (the original Laya prompt layout).

INSTRUCTIONS, PHRASINGS_PREFIX/SUFFIX, NO_MATCH_DESCRIPTION, `__none__`, [MASK] options, 48-token option cap,
head_max_len trimming and the json state follow the original Laya prompt format ("prod"). The compact formats
are the ones the released router was trained on. `python training/common.py` runs the self-checks.

Episode: {"id", "paths": [{"path_id", "text": [...]}], "message", "history"?, "gold", "teacher_probs"?}
`gold` is a path_id or "__none__". `teacher_probs` is {option_key: prob} (keys incl. "__none__").
"""

import json
import random

INSTRUCTIONS = (
    "A user sent this message to a conversational workflow that branches into the paths below. "
    "Which path is the message asking for?"
)
HISTORY_HINT = (
    " `history` holds the earlier turns of this conversation, oldest first; a short or elliptical "
    "message usually continues the intent of the most recent turns."
)
PHRASINGS_PREFIX = "Messages that mean the same as: "
PHRASINGS_SUFFIX = ", including typos, slang and paraphrases"
NO_MATCH_DESCRIPTION = "Gibberish, filler words, or a message unrelated to every other path."
NONE = "__none__"
OPTION_MAX_TOKENS = 48
MIN_HEAD_TOKENS = 16
MAX_LEN, HEAD_MAX_LEN = 512, 192
# option_format (recorded in rl_agent_config.json): "prod" = the original Laya prompt format;
# "compact" = `key: "p1" | "p2"` (no wrapper text), per-option cap 96. __none__ description unchanged.
# "compact_fill" = compact text and cap, but overflow is water-filled (see water_fill/fill_options)
# instead of cutting every option to the same share.
OPTION_FORMATS = {"prod": OPTION_MAX_TOKENS, "compact": 96, "compact_fill": 96}
COMPACT_FORMATS = ("compact", "compact_fill")
PHRASING_SEP = '" | "'  # boundary between two compact phrasings; a cut prefers to land right after its '"'


def no_match_key(paths) -> str:
    taken = {p["path_id"] for p in paths}
    key = NONE
    while key in taken:
        key += "_"
    return key


def describe(texts, option_format="prod") -> str:
    if option_format in COMPACT_FORMATS:
        return " | ".join(f'"{t}"' for t in texts)
    return PHRASINGS_PREFIX + ", ".join(f'"{t}"' for t in texts) + PHRASINGS_SUFFIX


def water_fill(lengths, budget, floor=4):
    """Token allowance per option. Options no longer than the fair share (budget // open options) keep
    their length; what they leave is re-split over the rest, repeated until stable. The remainder's +1s
    go to the earliest open options. `floor` mirrors compact's max(4, share)."""
    open_ = list(range(len(lengths)))
    while open_:
        fair = budget // len(open_)
        short = [i for i in open_ if lengths[i] <= fair]
        if not short:
            break
        budget -= sum(lengths[i] for i in short)
        open_ = [i for i in open_ if lengths[i] > fair]
    alloc = list(lengths)
    for j, i in enumerate(open_):
        alloc[i] = max(floor, budget // len(open_) + (j < budget % len(open_)))
    return alloc


def fill_options(tokenizer, mask, criteria, cap, head_max_len):
    """compact_fill option runs -> (options, cut_keys). Same as compact until the options crowd out the
    head; then each option gets its water_fill allowance, cut after the last whole phrasing when that
    loses <= 25% of the allowance, else at the token. cut_keys = paths (not the last, __none__) that
    lost phrasing text (a lost closing quote alone does not count)."""
    texts = [f" {k}: {d}".replace("[MASK]", " ") for k, d in criteria.items()]
    encs = [tokenizer.encode(t, add_special_tokens=False) for t in texts]
    options = [[mask] + e.ids[:cap] for e in encs]
    if head_max_len - sum(map(len, options)) < MIN_HEAD_TOKENS:
        alloc = water_fill([len(o) for o in options], head_max_len - MIN_HEAD_TOKENS)
        for i, (t, e, a) in enumerate(zip(texts, encs, alloc)):
            n = a - 1  # tokens after [MASK]
            if n >= len(options[i]) - 1:
                continue
            ends, keep = [end for _, end in e.offsets], n
            p = t.find(PHRASING_SEP)
            while p >= 0:  # boundaries in order; keep the last one that fits
                b = sum(x <= p + 1 for x in ends)  # tokens that end by the closing quote
                if b > n:
                    break
                if 4 * (n - b) <= a:
                    keep = b
                p = t.find(PHRASING_SEP, p + 1)
            options[i] = [mask] + e.ids[:keep]
    cut = []
    for k, t, e, o in list(zip(criteria, texts, encs, options))[:-1]:
        end = len(t) - 1 if t.endswith('"') else len(t)
        if len(o) - 1 < sum(s < end for s, _ in e.offsets):
            cut.append(k)
    return options, cut


def build_criteria(paths, none_key: str, option_format="prod") -> dict:
    c = {p["path_id"]: describe(p["text"], option_format) for p in paths}
    c[none_key] = NO_MATCH_DESCRIPTION
    return c


class Encoder:
    """`tokenizers.Tokenizer` wrapper that lays out one Choice question."""

    def __init__(self, tokenizer, max_len=MAX_LEN, head_max_len=HEAD_MAX_LEN, option_format="prod"):
        self.tok = tokenizer
        self.cls, self.sep, self.mask = (tokenizer.token_to_id(t) for t in ("[CLS]", "[SEP]", "[MASK]"))
        self.pad = tokenizer.token_to_id("[PAD]")
        assert None not in (self.cls, self.sep, self.mask, self.pad), "tokenizer lacks [CLS]/[SEP]/[MASK]/[PAD]"
        self.max_len, self.head_max_len = max_len, head_max_len
        self.option_format, self.option_max_tokens = option_format, OPTION_FORMATS[option_format]

    @classmethod
    def from_cfg(cls, tokenizer, cfg):
        return cls(tokenizer, cfg["max_len"], cfg["head_max_len"], cfg.get("option_format", "prod"))

    def _tokens(self, text, limit=None):
        ids = self.tok.encode(text.replace("[MASK]", " "), add_special_tokens=False).ids
        return ids[:limit] if limit else ids

    def options(self, criteria: dict, report=False):
        """criteria -> (option token runs, keys of paths whose phrasings were cut if report)."""
        if self.option_format == "compact_fill":
            return fill_options(self.tok, self.mask, criteria, self.option_max_tokens, self.head_max_len)
        options = [[self.mask] + self._tokens(f" {k}: {d}", self.option_max_tokens) for k, d in criteria.items()]
        if self.head_max_len - sum(map(len, options)) < MIN_HEAD_TOKENS:
            per = max(4, (self.head_max_len - MIN_HEAD_TOKENS) // len(options))
            options = [o[:per] for o in options]
        if not report:
            return options, None
        pairs = list(zip(criteria.items(), options))
        if self.option_format == "compact":  # every path option (the last one is __none__) that lost tokens
            cut = [k for (k, d), o in pairs[:-1] if len(o) - 1 < len(self._tokens(f" {k}: {d}"))]
        else:  # prod: cutting only the suffix does not count
            cut = [k for (k, d), o in pairs if d.startswith(PHRASINGS_PREFIX)
                   and len(o) - 1 < len(self._tokens(f" {k}: {d.removesuffix(PHRASINGS_SUFFIX)}"))]
        return options, cut

    def encode_criteria(self, state: dict, instructions: str, criteria: dict):
        """[CLS] instructions [SEP] ([MASK] option)... [SEP] state [SEP] -> (ids, markers)."""
        options, _ = self.options(criteria)
        head_room = self.head_max_len - sum(map(len, options))
        head = self._tokens(f"choice question: {instructions}")[: max(8, head_room)]
        ids = [self.cls, *head, self.sep]
        markers = []
        for o in options:
            markers.append(len(ids))
            ids += o
        ids.append(self.sep)
        room = max(0, self.max_len - len(ids) - 1)
        ids = (ids + self._tokens(json.dumps(state, ensure_ascii=False))[:room] + [self.sep])[: self.max_len]
        markers = [m for m in markers if m < self.max_len]
        if len(markers) != len(options):
            raise ValueError(f"options exceed max_len={self.max_len}")
        return ids, markers

    def encode(self, ep: dict, rng: random.Random | None = None) -> dict:
        """One episode -> {ids, markers, keys, label, target?}. `rng` shuffles path order (__none__ stays last)."""
        paths = list(ep["paths"])
        if rng is not None:
            rng.shuffle(paths)
        none_key = no_match_key(paths)
        criteria = build_criteria(paths, none_key, self.option_format)
        keys = list(criteria)
        state = {"message": ep["message"]}
        if ep.get("history"):
            state["history"] = list(ep["history"])
        instructions = INSTRUCTIONS + (HISTORY_HINT if ep.get("history") else "")
        ids, markers = self.encode_criteria(state, instructions, criteria)
        gold = none_key if ep["gold"] == NONE else ep["gold"]
        out = {"ids": ids, "markers": markers, "keys": keys, "label": keys.index(gold)}
        tp = ep.get("teacher_probs")
        if tp:
            t = [float(tp.get(NONE if k == none_key else k, 0.0)) for k in keys]
            s = sum(t)
            out["target"] = [v / s for v in t] if s > 0 else None
        return out


def load_tokenizer(path=None):
    from tokenizers import Tokenizer

    if path is None:
        from huggingface_hub import hf_hub_download

        path = hf_hub_download("convaiinnovations/laya", "tokenizer/tokenizer.json")
    return Tokenizer.from_file(path)


def _self_check(tok):
    """teacher_probs survive path shuffling, then the compact_fill cases."""
    order = [("order_status", ["where is my order", "track package"]), ("cancel_order", ["cancel my order"]),
             ("return_order", ["return item", "refund please"])]
    ep = {"paths": [{"path_id": p, "text": t} for p, t in order], "message": "cancel", "gold": "cancel_order",
          "teacher_probs": {"order_status": 0.1, "cancel_order": 0.8, "return_order": 0.05, NONE: 0.05}}
    e = Encoder(tok).encode(ep, random.Random(3))
    assert e["keys"][-1] == NONE and e["keys"][e["label"]] == "cancel_order"
    assert abs(e["target"][e["label"]] - 0.8) < 1e-9
    _fill_check(tok)


def _fill_check(tok):
    """compact_fill hand-built cases (a) no overflow == compact, (b) one long path + short ones."""
    assert water_fill([10, 10, 100], 60) == [10, 10, 40]
    assert water_fill([30, 30, 30], 61) == [21, 20, 20]  # equal share, remainder to the first
    assert water_fill([20, 28, 100], 81) == [20, 28, 33]  # 28 > 81//3 at first, fits after 20 is fixed
    assert water_fill([5, 5], 100) == [5, 5]
    comp, fill = Encoder(tok, MAX_LEN, 384, "compact"), Encoder(tok, MAX_LEN, 384, "compact_fill")

    def crit_of(paths):
        ps = [{"path_id": p, "text": t} for p, t in paths]
        return build_criteria(ps, no_match_key(ps), "compact_fill")

    # (a) no overflow, and an option over the 96 cap alone: identical to compact, nothing redistributed
    for paths in ([("a", ["hi", "hello"]), ("b", ["bye"])], [("a", ["word " * 150]), ("b", ["x"])]):
        c = crit_of(paths)
        assert fill.options(c)[0] == comp.options(c)[0]
        assert fill.encode_criteria({"message": "m"}, INSTRUCTIONS, c) == comp.encode_criteria({"message": "m"}, INSTRUCTIONS, c)
    assert fill.options(crit_of([("a", ["word " * 150]), ("b", ["x"])]), True)[1] == ["a"]  # the 96 cap cut it
    # (b) one long path + 6 short: short ones and __none__ untouched, the long one takes all that is left
    long_ = [f"long phrasing number {j} about moving money abroad" for j in range(30)]
    paths = [("wire", long_)] + [(f"s{i}", [f"short {i}", f"tiny {i}"]) for i in range(6)]
    c = crit_of(paths)
    small = Encoder(tok, MAX_LEN, 192, "compact_fill")  # 96-cap long + 7 short options overflow 192-16
    full = [[tok.token_to_id("[MASK]")] + small._tokens(f" {k}: {d}") for k, d in c.items()]
    opts, cut = small.options(c, True)
    assert opts[1:] == full[1:] and cut == ["wire"]
    left = 192 - MIN_HEAD_TOKENS - sum(map(len, full[1:]))
    assert opts[0] == full[0][: len(opts[0])] and left * 3 / 4 <= len(opts[0]) <= left
    assert tok.decode(opts[0][1:]).endswith('"')  # cut after a whole phrasing
    eq, _ = Encoder(tok, MAX_LEN, 192, "compact").options(c)
    assert len(eq[0]) == (192 - MIN_HEAD_TOKENS) // len(eq) < len(opts[0])  # compact: long one cut to the equal share
    ids, markers = small.encode_criteria({"message": "m"}, INSTRUCTIONS, c)
    assert markers[0] - 2 == 192 - sum(map(len, opts)) >= MIN_HEAD_TOKENS  # boundary slack goes back to the head
    print("compact_fill OK (water_fill, (a) no-overflow == compact, (b) long + short)")


if __name__ == "__main__":  # python training/common.py [tokenizer.json]
    import sys

    _self_check(load_tokenizer(sys.argv[1] if len(sys.argv) > 1 else None))
