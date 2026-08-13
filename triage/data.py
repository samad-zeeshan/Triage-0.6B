"""Load, split and format the support tickets, and parse what a model writes back.

Seeds and split sizes match the v1 notebooks so the committed train and test files rebuild byte for byte."""
import json
import random
import re
from pathlib import Path

import jsonschema
import pandas as pd
from sklearn.model_selection import train_test_split

SOURCE_URL = ("https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets/"
              "resolve/main/dataset-tickets-multi-lang-4-20k.csv")
CATEGORIES = ["Technical Support", "Product Support", "Customer Service",
              "Billing & Payments", "Returns & Exchanges"]
PRIORITIES = ["high", "medium", "low"]
FIELDS = ["category", "priority", "account_id"]

SYSTEM = (
    "Classify the support email. Respond with ONLY a JSON object with keys "
    '"category", "priority", and "account_id".\n'
    "category: one of Technical Support, Product Support, Customer Service, "
    "Billing & Payments, Returns & Exchanges.\n"
    "priority: one of high, medium, low.\n"
    'account_id: the account number stated in the email as a string, or null if none.'
)

SCHEMA = {
    "type": "object",
    "properties": {
        "category": {"enum": CATEGORIES},
        "priority": {"enum": PRIORITIES},
        "account_id": {"anyOf": [{"type": "string", "maxLength": 24}, {"type": "null"}]},
    },
    "required": FIELDS,
    "additionalProperties": False,
}

QUEUE_TO_CATEGORY = {
    "Technical Support": "Technical Support",
    "IT Support": "Technical Support",
    "Service Outages and Maintenance": "Technical Support",
    "Product Support": "Product Support",
    "Customer Service": "Customer Service",
    "General Inquiry": "Customer Service",
    "Human Resources": "Customer Service",
    "Billing and Payments": "Billing & Payments",
    "Sales and Pre-Sales": "Billing & Payments",
    "Returns and Exchanges": "Returns & Exchanges",
}

EN_ID = ["For reference, my account ends in {id}.",
         "Same account I always use, the one ending {id}.",
         "My account number is {id}.",
         "Please pull up account {id}."]
DE_ID = ["Zur Info, mein Konto endet auf {id}.",
         "Dasselbe Konto wie immer, endet auf {id}.",
         "Meine Kontonummer ist {id}."]


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def email_text(subject, body):
    return f"Subject: {subject}\n\nEmail: {body}"


def prompt(email, system=SYSTEM):
    """Qwen3 chat prompt exactly as training saw it, with thinking switched off."""
    return (f"<|im_start|>system\n{system}<|im_end|>\n"
            f"<|im_start|>user\n{email}<|im_end|>\n"
            "<|im_start|>assistant\n<think>\n\n</think>\n\n")


def load_chat(path):
    split = Path(path).stem.split("_")[0]
    rows = []
    for i, rec in enumerate(read_jsonl(path)):
        msgs = {m["role"]: m["content"] for m in rec["messages"]}
        rows.append({"id": f"{split}-{i:04d}", "email": msgs["user"],
                     "gold": json.loads(msgs["assistant"]) if "assistant" in msgs else None})
    return rows


def load_source(path):
    df = pd.read_csv(path)
    df["category"] = df["queue"].map(QUEUE_TO_CATEGORY)
    cols = ["subject", "body", "category", "priority", "language"]
    return df[cols].dropna(subset=["body", "category", "priority"]).reset_index(drop=True)


def augment(frame, rng, p_has_id=0.7):
    """Append an account sentence to about 70 percent of emails.

    The draw order (random, randint, choice) must match notebook 01, otherwise the
    injected numbers drift from what the teacher labelled."""
    frame = frame.copy().reset_index(drop=True)
    bodies, ids = [], []
    for r in frame.itertuples():
        body = str(r.body).strip()
        acct = None
        if rng.random() <= p_has_id:
            acct = str(rng.randint(1000, 99999))
            templates = DE_ID if str(r.language).lower().startswith("de") else EN_ID
            body = body + " " + rng.choice(templates).format(id=acct)
        bodies.append(body)
        ids.append(acct)
    frame["body_aug"] = bodies
    frame["account_id_true"] = ids
    return frame


def build_splits(data, val_size=600):
    pool, test = train_test_split(data, test_size=1200, stratify=data["category"], random_state=42)
    train, rest = train_test_split(pool, train_size=2500, stratify=pool["category"], random_state=42)
    # v1 augmented train then test from one seeded stream. The validation split is new
    # in v2, so it gets its own stream and cannot shift the committed files.
    rng = random.Random(42)
    train, test = augment(train, rng), augment(test, rng)
    _, val = train_test_split(rest, test_size=val_size, stratify=rest["category"], random_state=7)
    return train, test, augment(val, random.Random(7))


def _lenient(text):
    for m in re.finditer(r"\{[^{}]*\}", text):
        try:
            obj = json.loads(m.group(0))
        except ValueError:
            continue
        if isinstance(obj, dict) and ("priority" in obj or "category" in obj):
            return obj
    return {}


def parse_output(text):
    """Score structure and content separately, as in the two-axis study.

    Content falls back to the first JSON-looking object in the text, the same rule the
    v1 eval used, so a model is not scored zero on content for chatter around the JSON."""
    try:
        obj = json.loads(text.strip())
        json_valid = isinstance(obj, dict)
    except ValueError:
        obj, json_valid = None, False
    schema_valid = False
    if json_valid:
        try:
            jsonschema.validate(obj, SCHEMA)
            schema_valid = True
        except jsonschema.ValidationError:
            pass
    src = obj if json_valid else _lenient(text)
    pri = src.get("priority")
    acct = src.get("account_id")
    fields = {
        "category": src.get("category") if isinstance(src.get("category"), str) else None,
        "priority": pri.lower() if isinstance(pri, str) else None,
        "account_id": str(acct) if acct is not None and not isinstance(acct, (dict, list)) else None,
    }
    return {"json_valid": json_valid, "schema_valid": schema_valid, "fields": fields}
