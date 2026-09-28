"""Convert public English intent datasets into pseudo-workflow JSONL (data/public/).

Run:  uvx --with pandas --with pyarrow python training/public_data.py   (check() asserts run on every output)
Raw files are cached under scratch/raw/ and can be deleted afterwards.
Train workflows use only each dataset's train split. <name>_test.jsonl uses test-split
messages with phrasings drawn from train utterances (few-shot style benchmark).
"""
import glob, hashlib, json, random, re, sys, urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "scratch/raw", ROOT / "data/public"
HF = "https://huggingface.co/datasets"
URLS = {
    "data_full.json": "https://raw.githubusercontent.com/clinc/oos-eval/master/data/data_full.json",
    "b77_train.csv": "https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/master/banking_data/train.csv",
    "b77_test.csv": "https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/master/banking_data/test.csv",
    "hwu_train.parquet": f"{HF}/FastFit/hwu_64/resolve/main/data/train-00000-of-00001.parquet",
    "hwu_test.parquet": f"{HF}/FastFit/hwu_64/resolve/main/data/test-00000-of-00001.parquet",
    "snips_train.parquet": f"{HF}/benayas/snips/resolve/main/data/train-00000-of-00001.parquet",
    "snips_test.parquet": f"{HF}/benayas/snips/resolve/main/data/test-00000-of-00001.parquet",
    "bx_cs.csv": f"{HF}/bitext/Bitext-customer-support-llm-chatbot-training-dataset/resolve/main/Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11.csv",
    "bx_ecom.csv": f"{HF}/bitext/Bitext-retail-ecommerce-llm-chatbot-training-dataset/resolve/main/bitext-retail-ecommerce-llm-chatbot-training-dataset.csv",
    "bx_bank.parquet": f"{HF}/bitext/Bitext-retail-banking-llm-chatbot-training-dataset/resolve/main/bitext-retail-banking-llm-chatbot-training-dataset.parquet",
}

# Held-out domains (insurance claims, telecom carrier): drop any utterance that smells of them.
HELD_OUT_RE = re.compile(r"\binsur|\bclaims?\b|\bsim\b|\broaming\b|\bdata plan|\bcarrier\b|\bmobile plan|\bphone plan|\bprepaid\b|\bpostpaid\b", re.I)
DROP_INTENTS = {"insurance", "insurance_change", "general_quirky"}  # held-out domain / HWU junk catch-all

# SAME: practically indistinguishable, never in one workflow. NEAR: allowed together (tagged near_duplicate).
# Both: never used as each other's missing_intent __none__ (the gold would be arguable).
SAME = [
    {"availability", "availability_in_store", "availability_online"},
    {"return_product", "return_product_in_store", "return_product_online"},
    {"exchange_product", "exchange_product_in_store"},
    {"human_agent", "customer_service", "contact_customer_service", "contact_human_agent"},
    {"submit_feedback", "submit_product_feedback", "review"},
    {"track_order", "track_delivery"},
    {"get_invoice", "check_invoice", "request_invoice"},
    {"get_refund", "request_refund"},
    {"cancel_card", "block_card"},
    {"check_fees", "check_card_annual_fee"},
]
NEAR = [
    {"credit_limit", "credit_limit_change"}, {"pto_request", "pto_request_status", "pto_balance", "pto_used"},
    {"todo_list", "todo_list_update"}, {"shopping_list", "shopping_list_update"}, {"reminder", "reminder_update"},
    {"calendar", "calendar_update"}, {"oil_change_how", "oil_change_when"}, {"credit_score", "improve_credit_score"},
    {"travel_alert", "travel_notification"}, {"report_lost_card", "damaged_card", "new_card", "replacement_card_duration"},
    {"card_arrival", "card_delivery_estimate"}, {"pending_top_up", "top_up_failed", "top_up_reverted", "verify_top_up"},
    {"pending_transfer", "transfer_not_received_by_recipient", "transfer_timing", "balance_not_updated_after_bank_transfer", "failed_transfer"},
    {"pending_card_payment", "card_payment_not_recognised", "reverted_card_payment", "transaction_charged_twice"},
    {"declined_card_payment", "card_not_working", "declined_transfer", "declined_cash_withdrawal", "virtual_card_not_working", "contactless_not_working"},
    {"lost_or_stolen_card", "compromised_card", "card_swallowed"}, {"why_verify_identity", "verify_my_identity", "unable_to_verify_identity"},
    {"pending_cash_withdrawal", "cash_withdrawal_not_recognised", "wrong_amount_of_cash_received"},
    {"extra_charge_on_statement", "card_payment_fee_charged", "transfer_fee_charged", "cash_withdrawal_charge", "exchange_charge"},
    {"exchange_rate", "card_payment_wrong_exchange_rate", "wrong_exchange_rate_for_cash_withdrawal"},
    {"refund_not_showing_up", "request_refund", "refund_status", "track_refund"},
    {"topping_up_by_card", "top_up_by_card_charge"}, {"getting_virtual_card", "get_disposable_virtual_card"},
    {"get_physical_card", "order_physical_card", "getting_spare_card"},
    {"cancel_order", "change_order"}, {"delivery_period", "delivery_time", "delivery_options", "shipping_costs"},
    {"refund_policy", "return_policy", "check_refund_policy"}, {"damaged_delivery", "product_issue", "wrong_item", "missing_item"},
    {"close_account", "delete_account", "terminate_account"}, {"cancel_loan", "cancel_mortgage"},
    {"check_loan_payments", "check_mortgage_payments"}, {"apply_for_loan", "apply_for_mortgage"},
    {"iot_hue_lightdim", "iot_hue_lightup", "iot_hue_lightchange"}, {"audio_volume_down", "audio_volume_mute", "audio_volume_up"},
    {"play_music", "music_query", "music_settings"}, {"general_affirm", "general_confirm"},
    {"email_query", "email_querycontact"}, {"transport_query", "transport_ticket"},
]
GROUP_OF = {}
for kind, groups in (("same", SAME), ("near", NEAR)):
    for gi, g in enumerate(groups):
        for i in g:
            GROUP_OF.setdefault(i, set()).add((kind, gi))

BITEXT_TAGS = {"Z": "typo", "Q": "slang", "P": "polite", "W": "angry", "I": "question", "K": "short"}
VERBS = set("activate add apply block book cancel change check close contact create delete dispute edit exchange find get "
            "make order pay place recover remove report request reset return schedule set share submit switch sync track "
            "transfer update use verify track play freeze redeem rollover improve order_checks".split())
ENTITIES = {
    "{{Order Number}}": lambda r: f"{r.choice(['#', '', 'ORD-'])}{r.randint(10000, 9999999)}",
    "{{Invoice Number}}": lambda r: f"INV-{r.randint(1000, 999999)}",
    "{{Person Name}}": lambda r: r.choice(["Sarah Johnson", "Mike Chen", "Priya Patel", "John Smith", "Maria Garcia", "Ahmed Khan"]),
    "{{Refund Amount}}": lambda r: f"{r.randint(5, 900)}",
    "{{Currency Symbol}}": lambda r: r.choice(["$", "£", "€"]),
    "{{Delivery City}}": lambda r: r.choice(["Chicago", "Leeds", "Toronto", "Austin", "Dublin", "Sydney"]),
    "{{Delivery Country}}": lambda r: r.choice(["Canada", "Germany", "the UK", "Australia", "Mexico"]),
    "{{Account Type}}": lambda r: r.choice(["premium", "standard", "business", "free"]),
    "{{Account Category}}": lambda r: r.choice(["gold", "platinum", "basic", "pro"]),
}
PH_RE = re.compile(r"\{\{[^}]+\}\}")


def fetch(name):
    p = RAW / name
    if not p.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        print("download", name)
        urllib.request.urlretrieve(URLS[name], p)
    return p


def snake(s):
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", "_", s.strip().rstrip("?"))
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def norm(t):
    return re.sub(r"\s+", " ", t.lower()).strip(" .?!")


def hash_test(t):  # deterministic 10% test split for datasets without one
    return int(hashlib.md5(norm(t).encode()).hexdigest(), 16) % 10 == 0


# ---- loaders: return (train_rows, test_rows, oos_train, oos_test); rows = (intent, text, tags) ----
def load_clinc():
    d = json.load(open(fetch("data_full.json")))
    f = lambda k: [(i, t, []) for t, i in d[k]]
    return f("train"), f("test"), [t for t, _ in d["oos_train"]], [t for t, _ in d["oos_test"]]


def load_b77():
    f = lambda n: [(snake(c), t, []) for t, c in pd.read_csv(fetch(n))[["text", "category"]].itertuples(index=False)]
    return f("b77_train.csv"), f("b77_test.csv"), None, None


def load_parquet(prefix, col):
    f = lambda s: [(snake(c), t, []) for t, c in pd.read_parquet(fetch(f"{prefix}_{s}.parquet"))[["text", col]].itertuples(index=False)]
    return f("train"), f("test"), None, None


def load_bitext(name, tagcol):
    p = fetch(name)
    df = pd.read_parquet(p) if name.endswith("parquet") else pd.read_csv(p)
    rows = [(snake(i), t, sorted({BITEXT_TAGS[c] for c in str(fl) if c in BITEXT_TAGS}))
            for t, i, fl in df[["instruction", "intent", tagcol]].itertuples(index=False)]
    rows = [r for r in rows if r[1].isascii()]  # English rows only (all rows are English today)
    return [r for r in rows if not hash_test(r[1])], [r for r in rows if hash_test(r[1])], None, None


# name -> (loader, domain, use CLINC oos as off-topic __none__, train message budget)
DATASETS = {
    "clinc150": (load_clinc, "general_assistant", True, 16000),
    "banking77": (load_b77, "banking", True, 13000),
    "hwu64": (lambda: load_parquet("hwu", "label"), "home_assistant", False, 10000),  # CLINC oos overlaps HWU qa/news intents
    "snips": (lambda: load_parquet("snips", "category"), "media_and_local", True, 5000),
    "bitext_customer_support": (lambda: load_bitext("bx_cs.csv", "flags"), "customer_support", True, 13000),
    "bitext_retail_ecommerce": (lambda: load_bitext("bx_ecom.csv", "tags"), "ecommerce", True, 14000),
    "bitext_retail_banking": (lambda: load_bitext("bx_bank.parquet", "tags"), "banking", True, 12000),
}


def eval_texts():
    seen = set()
    for f in glob.glob(str(ROOT / "data/eval/*.jsonl")):
        for line in open(f):
            w = json.loads(line)
            seen |= {norm(m["text"]) for m in w["messages"]}
            seen |= {norm(t) for p in w["paths"] for t in p["text"]}
    return seen


def group(rows, banned):
    by = {}
    for intent, text, tags in rows:
        if intent in DROP_INTENTS or HELD_OUT_RE.search(text) or norm(text) in banned:
            continue
        d = by.setdefault(intent, {})
        d.setdefault(norm(text), (text.strip(), tags))
    return {i: list(v.values()) for i, v in by.items() if len(v) >= 3}


def fill(text, r):
    return PH_RE.sub(lambda m: ENTITIES.get(m.group(0), lambda r: "123")(r), text)


def describe(intent, r):
    words = intent.replace("_", " ")
    if words.split()[0] in VERBS:
        return r.choice(["Customer wants to ", "User wants to ", "The customer asks to "]) + words
    return r.choice(["Customer asks about ", "Questions about ", "User needs help with "]) + words


def auto_tags(text):
    t = []
    if len(text.split()) <= 3: t.append("short")
    if text.rstrip().endswith("?") or re.match(r"(?i)(what|how|why|when|where|who|can|could|is|are|do|does|will)\b", text): t.append("question")
    if re.search(r"[.!?]\s+\w", text.strip()): t.append("multi_sentence")
    if re.search(r"\d", text): t.append("entity")
    return t


def conflicts(a, b, kinds):
    return any(k in kinds and (k, g) in GROUP_OF.get(b, ()) for k, g in GROUP_OF.get(a, ()))


def build(name, domain, phr_pool, msg_pool, oos, budget, r, tag):
    """phr_pool: intent -> utterances for phrasings; msg_pool: intent -> utterances for messages."""
    intents = sorted(set(phr_pool) & set(msg_pool))
    out, n_msgs, i = [], 0, 0
    while n_msgs < budget:
        k = min(r.randint(2, 15), max(2, len(intents) - 2))  # leave room for missing_intent
        paths = []
        for it in r.sample(intents, len(intents)):
            if len(paths) == k: break
            if not any(conflicts(it, p, ("same",)) for p in paths):
                paths.append(it)
        used, wf_paths = set(), []
        for it in paths:
            # configs use short phrasings and share a 192-token head budget: prefer <=15 words, no placeholders
            cands = [u for u in phr_pool[it] if not PH_RE.search(u[0]) and len(u[0].split()) <= 15] or phr_pool[it]
            phr = [fill(t, r) for t, _ in r.sample(cands, min(r.randint(1, 8), len(cands)))]
            if r.random() < 0.3:
                phr[r.randrange(len(phr))] = describe(it, r)
            phr = list(dict.fromkeys(phr))
            used |= {norm(p) for p in phr}
            wf_paths.append({"path_id": it, "text": phr})
        msgs = []
        for it in paths:
            for _ in range(r.choice([0, 1, 1, 1, 2]) if len(paths) > 4 else r.choice([1, 1, 2, 3])):
                raw, tg = r.choice(msg_pool[it])
                t = fill(raw, r)
                if norm(t) in used: continue
                used.add(norm(t))
                tags = set(tg) | set(auto_tags(t)) | ({"entity"} if PH_RE.search(raw) else set())
                if any(conflicts(it, p, ("near",)) for p in paths if p != it): tags.add("near_duplicate")
                msgs.append({"text": t, "gold": it, "tags": sorted(tags)})
        if r.random() < 0.4:
            missing = [m for m in intents if m not in paths and not any(m == p or conflicts(m, p, ("same", "near")) for p in paths)]
            for it in r.sample(missing, min(r.randint(1, 2), len(missing))):
                raw, tg = r.choice(msg_pool[it])
                t = fill(raw, r)
                if norm(t) not in used:
                    used.add(norm(t))
                    tags = {"missing_intent", *tg, *auto_tags(t)} | ({"entity"} if PH_RE.search(raw) else set())
                    msgs.append({"text": t, "gold": "__none__", "tags": sorted(tags)})
        if oos and r.random() < 0.35:
            t = r.choice(oos)
            if norm(t) not in used:
                msgs.append({"text": t, "gold": "__none__", "tags": sorted({"off_topic", *auto_tags(t)})})
        if not any(m["gold"] != "__none__" for m in msgs):
            continue
        r.shuffle(msgs)
        out.append({"workflow_id": f"{name}{tag}-{i:06d}", "domain": domain, "source": f"public:{name}", "paths": wf_paths, "messages": msgs})
        n_msgs += len(msgs)
        i += 1
    return out


def write(path, wfs):
    with open(path, "w") as f:
        for w in wfs:
            f.write(json.dumps(w, ensure_ascii=False) + "\n")


def stats(wfs):
    msgs = [m for w in wfs for m in w["messages"]]
    return {"workflows": len(wfs), "messages": len(msgs), "none": sum(m["gold"] == "__none__" for m in msgs),
            "missing_intent_wf_pct": round(100 * sum(any("missing_intent" in m["tags"] for m in w["messages"]) for w in wfs) / max(1, len(wfs)), 1)}


def check(wfs):
    for w in wfs:
        ids = {p["path_id"] for p in w["paths"]}
        phr = {norm(t) for p in w["paths"] for t in p["text"]}
        assert 2 <= len(ids) <= 15 and len(ids) == len(w["paths"]), w["workflow_id"]
        assert all(1 <= len(p["text"]) <= 8 for p in w["paths"]), w["workflow_id"]
        for m in w["messages"]:
            assert m["gold"] in ids or m["gold"] == "__none__", w["workflow_id"]
            assert norm(m["text"]) not in phr, (w["workflow_id"], m["text"])
            assert "{{" not in m["text"] and not HELD_OUT_RE.search(m["text"])
        for a in ids:
            assert not any(conflicts(a, b, ("same",)) for b in ids if b != a), w["workflow_id"]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    banned = eval_texts()
    summary = {}
    for name, (loader, domain, use_oos, budget) in DATASETS.items():
        r = random.Random(name)
        tr, te, oos_tr, oos_te = loader()
        if use_oos and oos_tr is None:  # borrow CLINC's OOS pool
            _, _, oos_tr, oos_te = load_clinc()
        oos_tr = [t for t in (oos_tr or []) if not HELD_OUT_RE.search(t) and norm(t) not in banned] if use_oos else None
        oos_te = [t for t in (oos_te or []) if not HELD_OUT_RE.search(t)] if use_oos else None
        gtr, gte = group(tr, banned), group(te, set())
        train = build(name, domain, gtr, gtr, oos_tr, budget, r, "")
        test = build(name, domain, gtr, gte, oos_te, min(3000, sum(map(len, gte.values()))), r, "-test")
        check(train); check(test)
        write(OUT / f"{name}.jsonl", train); write(OUT / f"{name}_test.jsonl", test)
        summary[name] = {"intents": len(gtr), "train": stats(train), "test": stats(test)}
        print(name, summary[name], flush=True)
    json.dump(summary, open(OUT / "stats.json", "w"), indent=1)


if __name__ == "__main__":
    main()
