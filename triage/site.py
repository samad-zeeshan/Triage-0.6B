"""Build the data file for the static demo in site/ from recorded runs and result files.

The page never runs a model. Every answer it shows is a line from eval/runs."""
import json
import random
import shutil
from pathlib import Path

import numpy as np

from triage import calibrate, data

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def _calibrated(logits, pred, temps):
    conf = {}
    for field, options in (("category", data.CATEGORIES), ("priority", data.PRIORITIES)):
        p = calibrate.softmax(np.array([logits[field]]), temps[field])[0]
        conf[field] = {"probs": {o: round(float(v), 4) for o, v in zip(options, p)},
                       "chosen": round(float(p[options.index(pred[field])]), 4) if pred[field] in options else 0.0}
    return conf


def _entry(kind, rid, email, pred, logits, acct_conf, temps, threshold, gold=None, teacher=None, note=None):
    conf = _calibrated(logits, pred, temps)
    ticket = min(conf["category"]["chosen"], conf["priority"]["chosen"])
    return {"kind": kind, "id": rid, "email": email, "pred": pred, "confidence": conf,
            "account_confidence": round(float(acct_conf), 4), "ticket_confidence": round(ticket, 4),
            "escalate": ticket < threshold, "gold": gold, "teacher": teacher, "note": note}


def build():
    res = {n: json.loads((ROOT / f"eval/results/{n}.json").read_text(encoding="utf-8"))
           for n in ("headline", "cascade", "calibration", "quantization", "trust", "decoding")}
    cas = res["cascade"]
    temps, threshold = cas["temperatures"], cas["threshold"]
    level = cas["level"]
    emails = {r["id"]: r["email"] for r in data.load_chat(ROOT / "data/test_chat.jsonl")}
    teacher = {r["id"]: r["label"] for r in data.read_jsonl(ROOT / "data/test_teacher_2026.jsonl")}
    rows = data.read_jsonl(ROOT / f"eval/runs/{level}-test.jsonl")

    def make(r, kind, note=None):
        pred = r["modes"]["native"]["pred"]
        return _entry(kind, r["id"], emails[r["id"]], pred, r["logits"], r["conf"]["account_id"],
                      temps, threshold, gold=r["gold"], teacher=teacher[r["id"]], note=note)

    entries = [make(r, "ticket") for r in rows]
    # Some source rows have no subject and read "Subject: nan". They stay in the
    # picker, but the featured examples should not lead with a data gap.
    short = [e for e in entries if len(e["email"]) < 700 and "Subject: nan" not in e["email"]]
    easy = max((e for e in short if not e["escalate"] and e["pred"] == e["gold"]), key=lambda e: e["ticket_confidence"])
    kept = [e for e in short if not e["escalate"]]
    # The ambiguous example is the least sure ticket the small model still keeps.
    ambiguous = min(kept, key=lambda e: e["ticket_confidence"])
    wrong_fixed = [e for e in short if e["escalate"] and e["pred"]["priority"] != e["gold"]["priority"]
                   and e["teacher"] and e["teacher"]["priority"] == e["gold"]["priority"]]
    escalated = min(wrong_fixed or [e for e in short if e["escalate"]], key=lambda e: e["ticket_confidence"])
    trust_rows = data.read_jsonl(ROOT / f"eval/runs/trust-{level}.jsonl")
    from triage.trust import OFF_TASK
    offs = [_entry("off-task", r["id"], OFF_TASK[int(r["id"].split("-")[1])], r["pred"], r["logits"],
                   r["conf"]["account_id"], temps, threshold)
            for r in trust_rows if r["suite"] == "off_task"]
    # Show the off-task input the model is surest about, since that is the case the
    # threshold does not catch.
    off_entry = max(offs, key=lambda e: e["ticket_confidence"])
    off_entry["note"] = ("Not a support email. The model still answers in the ticket format, "
                         + ("and the cascade sends it to the teacher." if off_entry["escalate"]
                            else "and is sure enough that the cascade keeps it."))

    picks = random.Random(3).sample(entries, 24)
    featured = {"easy": easy, "ambiguous": ambiguous, "escalated": escalated, "off_task": off_entry}
    per_ticket = cas["teacher"]["cost_per_ticket_usd"]
    h = res["headline"]
    out = {
        "level": level, "threshold": threshold, "temperatures": temps,
        "teacher": {"served": cas["teacher"]["served"], "cost_per_ticket": per_ticket},
        "cost_per_1000": {"small": 0.0, "cascade": cas["chosen"]["cost_per_1000"], "teacher": cas["teacher_only"]["cost_per_1000"]},
        "escalated_share": cas["chosen"]["escalated"],
        "headline": {"base_priority": h["base"]["priority"]["acc"], "tuned_priority": h["tuned"]["priority"]["acc"],
                     "tuned_priority_ci": h["tuned"]["priority"]["ci"], "trivial_priority": h["trivial"]["priority"]["acc"],
                     "v1_priority": h["v1"]["tuned_priority"]},
        "cascade": {"student": cas["student_only"], "chosen": cas["chosen"], "teacher": cas["teacher_only"]},
        "featured": featured,
        "tickets": sorted(picks, key=lambda e: e["id"]),
    }
    (SITE / "data").mkdir(parents=True, exist_ok=True)
    text = json.dumps(out, indent=1, ensure_ascii=False)
    (SITE / "data/demo.json").write_text(text + "\n", encoding="utf-8")
    (SITE / "data/demo.js").write_text(
        "window.DEMO_DATA = window.DEMO_DATA || {};\nwindow.DEMO_DATA[\"triage\"] = " + text + ";\n", encoding="utf-8")
    for svg in (ROOT / "eval/figures").glob("*.svg"):
        shutil.copy(svg, SITE / "data" / svg.name)
    return out


if __name__ == "__main__":
    build()
    print("site/data written")
