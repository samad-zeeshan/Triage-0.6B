"""Label emails with the hosted teacher model, caching every answer on disk.

The cache is committed, so every table can be rebuilt without an API key."""
import hashlib
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from triage import data

ROOT = Path(__file__).resolve().parents[1]

# Word for word the prompt notebook 01 sent, so new labels are comparable with v1 gold.
SYSTEM = """You label customer support emails. Output ONLY a JSON object with exactly these fields:
- "category": exactly one of: Technical Support | Product Support | Customer Service | Billing & Payments | Returns & Exchanges
- "priority": exactly one of: high | medium | low
    high   = outage, blocked from using the product, security/payment failure, or urgent business impact
    medium = a real problem needing action, but not blocking or time-critical
    low    = general question, minor request, feedback, or no urgency
- "account_id": the customer's account number if one is stated in the email, as a string; otherwise null. Never invent one.
Output only the JSON object."""


def cost_usd(tokens_in, tokens_out, cfg):
    return tokens_in * cfg["price_input_per_m"] / 1e6 + tokens_out * cfg["price_output_per_m"] / 1e6


def load_config():
    import yaml
    return yaml.safe_load(open(ROOT / "configs/teacher.yaml", encoding="utf-8"))


class Teacher:
    def __init__(self, cfg, cache=ROOT / "data/teacher_cache.jsonl", client=None, system=SYSTEM):
        self.cfg, self.system, self.client = cfg, system, client
        self.cache_path = Path(cache) if cache else None
        self.cache = {}
        if self.cache_path and self.cache_path.exists():
            self.cache = {r["key"]: r for r in data.read_jsonl(self.cache_path)}
        self.lock = threading.Lock()

    def _client(self):
        if self.client is None:
            key = os.environ.get(self.cfg["key_env"])
            if not key:
                raise RuntimeError(f"set {self.cfg['key_env']} to call the teacher, "
                                   "or use the cached labels already in data/")
            from openai import OpenAI
            self.client = OpenAI(api_key=key, base_url=self.cfg.get("base_url"))
        return self.client

    def key(self, email):
        raw = json.dumps([self.cfg["model"], self.system, email], ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

    def label(self, email, json_mode=True):
        k = self.key(email)
        if k in self.cache:
            return self.cache[k]
        kwargs = {"response_format": {"type": "json_object"}} if json_mode else {}
        r = self._client().chat.completions.create(
            model=self.cfg["model"], temperature=0,
            messages=[{"role": "system", "content": self.system},
                      {"role": "user", "content": email}], **kwargs)
        text = r.choices[0].message.content
        try:
            parsed = json.loads(text) if json_mode else text
        except ValueError:
            parsed = None
        rec = {"key": k, "label": parsed, "served_model": r.model,
               "tokens_in": r.usage.prompt_tokens, "tokens_out": r.usage.completion_tokens}
        with self.lock:
            self.cache[k] = rec
            if self.cache_path:
                with open(self.cache_path, "a", encoding="utf-8", newline="\n") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return rec

    def label_many(self, emails, json_mode=True):
        with ThreadPoolExecutor(self.cfg.get("workers", 4)) as pool:
            return list(pool.map(lambda e: self.label(e, json_mode), emails))


def main():
    """Label the validation split and relabel the test split with today's teacher."""
    cfg = load_config()
    teacher = Teacher(cfg)
    for name, rows in (("val", data.read_jsonl(ROOT / "data/val_emails.jsonl")),
                       ("test", data.load_chat(ROOT / "data/test_chat.jsonl"))):
        recs = teacher.label_many([r["email"] for r in rows])
        out = [{"id": r["id"], "label": rec["label"], "served_model": rec["served_model"],
                "tokens_in": rec["tokens_in"], "tokens_out": rec["tokens_out"]}
               for r, rec in zip(rows, recs)]
        data.write_jsonl(ROOT / f"data/{name}_teacher_2026.jsonl", out)
        print(name, len(out), "labelled")


if __name__ == "__main__":
    main()
