"""Render the README result tables from eval/results and write them between their markers.

`python -m triage.readme --check` exits non-zero when the README has drifted from the results."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "eval/results"
README = ROOT / "README.md"


def _r(name):
    return json.loads((RESULTS / f"{name}.json").read_text(encoding="utf-8"))


def _ci(block):
    return f"{block['acc']:.1f} ({block['ci'][0]:.1f} to {block['ci'][1]:.1f})"


def _p(p):
    return "below 0.001" if p < 0.001 else f"{p:.3f}"


def headline():
    h = _r("headline")
    t, b, v1 = h["tuned"], h["base"], h["v1"]
    rows = [
        ("Priority", v1["tuned_priority"], _ci(t["priority"]), _ci(b["priority"]), f"{h['trivial']['priority']['acc']:.1f} (always high)"),
        ("Category", v1["tuned_category"], _ci(t["category"]), _ci(b["category"]), f"{h['trivial']['category']['acc']:.1f} (always Technical Support)"),
        ("Account number", "not scored", _ci(t["account_id"]), _ci(b["account_id"]), f"{h['trivial']['account_id']['acc']:.1f} (always none)"),
        ("Valid JSON, v1 rule", v1["tuned_valid_json"], _ci(t["valid_json_v1_rule"]), _ci(b["valid_json_v1_rule"]), "n/a"),
        ("Exact schema", "not scored", _ci(t["schema_valid"]), _ci(b["schema_valid"]), "n/a"),
    ]
    out = ["| Percent correct, 1,200 held-out tickets | v1 fine-tuned | v2 fine-tuned, 95% interval | Base model | Trivial |",
           "|---|---|---|---|---|"]
    out += [f"| {a} | {b_} | {c} | {d} | {e} |" for a, b_, c, d, e in rows]
    vs = h["vs"]
    out.append("")
    out.append(f"Fine-tuned against trivial on priority: +{vs['trivial']['priority']['diff']:.1f} points "
               f"({vs['trivial']['priority']['ci'][0]:.1f} to {vs['trivial']['priority']['ci'][1]:.1f}), McNemar p {_p(vs['trivial']['priority']['mcnemar_p'])}. "
               f"Against the base model: +{vs['base']['priority']['diff']:.1f} points "
               f"({vs['base']['priority']['ci'][0]:.1f} to {vs['base']['priority']['ci'][1]:.1f}), p {_p(vs['base']['priority']['mcnemar_p'])}.")
    return "\n".join(out)


def decoding():
    d = _r("decoding")
    out = ["| Model | Decoding | Exact schema | Category | Priority | Account number |", "|---|---|---|---|---|---|"]
    for model, name in (("base", "Base"), ("tuned", "Fine-tuned")):
        modes = (("native", "native"), ("outlines", "Outlines"), ("xgrammar", "XGrammar"))
        # Three identical rows say less than one row that says they are identical.
        if all(d[model][m].get("changed_vs_native", 0) == 0 for m, _ in modes[1:]) and all(
                d[model][m]["schema_valid"]["acc"] == d[model]["native"]["schema_valid"]["acc"] for m, _ in modes):
            modes = (("native", "all three, same answers"),)
        for mode, label in modes:
            m = d[model][mode]
            out.append(f"| {name} | {label} | {m['schema_valid']['acc']:.1f} | {m['category']['acc']:.1f} | "
                       f"{m['priority']['acc']:.1f} | {m['account_id']['acc']:.1f} |")
    return "\n".join(out)


def calibration():
    c = _r("calibration")
    out = ["| Field | Temperature | ECE before | ECE after | Brier before | Brier after |", "|---|---|---|---|---|---|"]
    for f in ("category", "priority"):
        x = c["fields"][f]
        out.append(f"| {f} | {x['temperature']:.2f} | {100 * x['before']['ece']:.1f} | {100 * x['after']['ece']:.1f} | "
                   f"{x['before']['brier']:.3f} | {x['after']['brier']:.3f} |")
    a = c["fields"]["account_id"]["before"]
    out.append(f"| account number | not rescaled | {100 * a['ece']:.1f} | n/a | n/a | n/a |")
    return "\n".join(out)


def cascade():
    c = _r("cascade")
    ch = c["chosen"]
    rows = [("Small model only", 0.0, c["student_only"]),
            (f"Cascade, threshold {c['threshold']:.3f}", ch["escalated"], {"acc": ch["acc"], "priority_acc": ch["priority_acc"],
                                                                         "category_acc": ch["category_acc"], "cost_per_1000": ch["cost_per_1000"]}),
            ("Teacher only", 1.0, c["teacher_only"])]
    out = ["| Route | Sent to teacher | Both right | Priority | Category | Teacher cost per 1,000 tickets |", "|---|---|---|---|---|---|"]
    for name, esc, x in rows:
        out.append(f"| {name} | {100 * esc:.1f}% | {100 * x['acc']:.1f} | {100 * x['priority_acc']:.1f} | "
                   f"{100 * x['category_acc']:.1f} | ${x['cost_per_1000']:.4f} |")
    return "\n".join(out)


def quantization():
    q = _r("quantization")
    names = {"f16": "F16", "q8_0": "Q8_0", "q6_k": "Q6_K", "q4_k_m": "Q4_K_M"}
    out = ["| File | MB | Priority | Category | Account number | Same answer as Q8_0 | ms per ticket, CPU | Leaks: completion, task, test control |",
           "|---|---|---|---|---|---|---|---|"]
    for level, name in names.items():
        b = q["levels"].get(level)
        if not b:
            continue
        leak = "n/a"
        if "leak_completion_train" in b:
            lt, lc = b["leak_completion_train"], b["leak_completion_test"]
            kt = b["leak_task_train"]
            leak = f"{lt['hits']}/{lt['n']}, {kt['hits']}/{kt['n']}, {lc['hits']}/{lc['n']}"
        lat = f"{b['latency_ms']:.0f}" if b.get("latency_ms") else "n/a"
        chosen = " (deployed)" if level == q["chosen"] else ""
        out.append(f"| {name}{chosen} | {b['size_mb']} | {b['priority']['acc']:.1f} | {b['category']['acc']:.1f} | "
                   f"{b['account_id']['acc']:.1f} | {100 * b['agrees_with_q8_0']:.1f}% | {lat} | {leak} |")
    return "\n".join(out)


def trust():
    t = _r("trust")
    b, a = t["base"], t["tuned"]
    rows = [
        ("Off-task input answered as a ticket (of 30)", b["off_task"]["schema_valid"], a["off_task"]["schema_valid"]),
        ("Off-task input the deployed cascade would keep (of 30)", "n/a", t["deployed_off_task"]["would_skip_teacher"]),
        ("Low-priority tickets pushed to high by an injected line (of 40)",
         f"{b['injection']['high_with_injection']} (was {b['injection']['high_without']})",
         f"{a['injection']['high_with_injection']} (was {a['injection']['high_without']})"),
        ("Priority accuracy with typos, 200 tickets", f"{100 * b['typo']['priority_acc']:.1f} (clean {100 * b['typo']['priority_acc_original']:.1f})",
         f"{100 * a['typo']['priority_acc']:.1f} (clean {100 * a['typo']['priority_acc_original']:.1f})"),
        ("Priority accuracy on paraphrases, 200 tickets", f"{100 * b['paraphrase']['priority_acc']:.1f} (clean {100 * b['paraphrase']['priority_acc_original']:.1f})",
         f"{100 * a['paraphrase']['priority_acc']:.1f} (clean {100 * a['paraphrase']['priority_acc_original']:.1f})"),
        ("Planted card, phone or SSN echoed in the output (of 50)", b["pii"]["echoed_any"], a["pii"]["echoed_any"]),
    ]
    out = ["| Check | Base model | Fine-tuned |", "|---|---|---|"]
    out += [f"| {n} | {x} | {y} |" for n, x, y in rows]
    return "\n".join(out)


def geometry():
    g = _r("geometry")
    out = ["| Neighbourhood of the ticket | Tickets | Priority right | Mean confidence |", "|---|---|---|---|"]
    for row in g["groups"]:
        out.append(f"| {row['neighbourhood']} | {row['n']} | {100 * row['priority_acc']:.1f} | {row['mean_confidence']:.2f} |")
    return "\n".join(out)


TABLES = {"headline": headline, "decoding": decoding, "calibration": calibration, "cascade": cascade,
          "quantization": quantization, "trust": trust, "geometry": geometry}


def render(text):
    for name, fn in TABLES.items():
        pattern = re.compile(rf"(<!-- table:{name} -->).*?(<!-- /table:{name} -->)", re.S)
        if pattern.search(text):
            body = fn()
            text = pattern.sub(lambda m: m.group(1) + "\n" + body + "\n" + m.group(2), text)
    return text


def main():
    text = README.read_text(encoding="utf-8")
    new = render(text)
    if "--check" in sys.argv:
        if new != text:
            print("README tables differ from eval/results, run `python -m triage.readme`")
            sys.exit(1)
        print("README matches eval/results")
        return
    README.write_text(new, encoding="utf-8", newline="\n")
    print("README tables updated")


if __name__ == "__main__":
    main()
