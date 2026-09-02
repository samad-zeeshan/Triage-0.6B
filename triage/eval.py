"""Turn the recorded runs in eval/runs into the result files in eval/results.

Nothing here calls a model, so CI can rebuild every table in seconds and fail on drift."""
import json
from pathlib import Path

import numpy as np
import yaml

from triage import calibrate, cascade, data, label, stats

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "eval/runs"
RESULTS = ROOT / "eval/results"
LEVELS = ["f16", "q8_0", "q6_k", "q4_k_m"]


def load_run(name):
    path = RUNS / f"{name}.jsonl"
    rows = data.read_jsonl(path)
    return sorted(rows, key=lambda r: r["id"])


def correct(rows, field, mode="native", gold=None):
    gold = gold or {r["id"]: r["gold"] for r in rows}
    return np.array([r["modes"][mode]["pred"][field] == gold[r["id"]][field] for r in rows], int)


def lenient_valid(rows, mode="native"):
    # v1 called an answer valid when a category and a priority could be pulled out of it.
    return np.array([bool(r["modes"][mode]["pred"]["category"]) and bool(r["modes"][mode]["pred"]["priority"])
                     for r in rows], int)


def _field_block(rows, mode="native"):
    out = {f: stats.summarise(correct(rows, f, mode)) for f in data.FIELDS}
    both = correct(rows, "category", mode) & correct(rows, "priority", mode)
    out["category_and_priority"] = stats.summarise(both)
    out["valid_json_v1_rule"] = stats.summarise(lenient_valid(rows, mode))
    out["schema_valid"] = stats.summarise(np.array([r["modes"][mode]["schema_valid"] for r in rows], int))
    return out


def headline():
    tuned, base = load_run("q8_0-test"), load_run("base-q8_0-test")
    gold = [r["gold"] for r in tuned]
    trivial = {
        "priority": np.array([g["priority"] == "high" for g in gold], int),
        "category": np.array([g["category"] == "Technical Support" for g in gold], int),
        "account_id": np.array([g["account_id"] is None for g in gold], int),
    }
    tests = {}
    for other_name, other in (("base", None), ("trivial", trivial)):
        tests[other_name] = {}
        for f in data.FIELDS:
            a = correct(tuned, f)
            b = correct(base, f) if other is None else other[f]
            lo, hi = stats.paired_diff_ci(a, b)
            tests[other_name][f] = {"diff": round(100 * float(a.mean() - b.mean()), 1),
                                    "ci": [round(100 * lo, 1), round(100 * hi, 1)],
                                    "mcnemar_p": stats.mcnemar(a, b)}
    v1 = stats.parse_v1(ROOT / "eval/v1/confusion_matrices.txt")
    tuned_block = _field_block(tuned)
    lo, hi = tuned_block["priority"]["ci"]
    return {
        "model": "triage-0.6b-q8_0.gguf, greedy, native decoding, CPU llama.cpp",
        "test_tickets": len(tuned),
        "tuned": tuned_block,
        "base": _field_block(base),
        "trivial": {f: stats.summarise(v) for f, v in trivial.items()},
        "vs": tests,
        "v1": v1,
        "v1_priority_inside_interval": lo <= v1["tuned_priority"] <= hi,
        "bootstrap": {"resamples": stats.B, "seed": stats.SEED, "level": 0.95},
    }


def decoding():
    out = {}
    for model, run in (("tuned", "q8_0-test"), ("base", "base-q8_0-test")):
        rows = load_run(run)
        out[model] = {}
        for mode in ("native", "outlines", "xgrammar"):
            block = {f: stats.summarise(correct(rows, f, mode)) for f in data.FIELDS}
            block["schema_valid"] = stats.summarise(np.array([r["modes"][mode]["schema_valid"] for r in rows], int))
            block["json_valid"] = stats.summarise(np.array([r["modes"][mode]["json_valid"] for r in rows], int))
            block["gen_ms_median"] = float(np.median([r["modes"][mode]["gen_ms"] for r in rows]))
            if mode != "native":
                block["changed_vs_native"] = int(sum(
                    r["modes"][mode]["pred"] != r["modes"]["native"]["pred"] for r in rows))
            out[model][mode] = block
    return out


def _val_arrays(run, gold_by_id):
    rows = [r for r in load_run(run) if gold_by_id.get(r["id"])]
    arrays = {}
    for f, options in (("category", data.CATEGORIES), ("priority", data.PRIORITIES)):
        keep = [r for r in rows if gold_by_id[r["id"]][f] in options]
        logits = np.array([r["logits"][f] for r in keep])
        y = np.array([options.index(gold_by_id[r["id"]][f]) for r in keep])
        arrays[f] = (logits, y, keep)
    return arrays


def val_gold():
    return {r["id"]: r["label"] for r in data.read_jsonl(ROOT / "data/val_teacher_2026.jsonl")}


def test_gold():
    return {r["id"]: r["gold"] for r in data.load_chat(ROOT / "data/test_chat.jsonl")}


def temperatures(level):
    val = _val_arrays(f"{level}-val", val_gold())
    return {f: calibrate.fit_temperature(val[f][0], val[f][1]) for f in val}


def calibration(level):
    temps = temperatures(level)
    test = _val_arrays(f"{level}-test", test_gold())
    out = {"level": level, "fitted_on": "validation split, 600 tickets, 2026 teacher labels", "fields": {}}
    for f, (logits, y, rows) in test.items():
        before = calibrate.field_metrics(logits, y, 1.0)
        after = calibrate.field_metrics(logits, y, temps[f])
        greedy = [r["modes"]["native"]["pred"][f] for r in rows]
        options = data.CATEGORIES if f == "category" else data.PRIORITIES
        argmax = [options[i] for i in logits.argmax(1)]
        out["fields"][f] = {"temperature": round(temps[f], 3), "before": before, "after": after,
                            "readout_agrees_with_greedy": round(float(np.mean([a == b for a, b in zip(greedy, argmax)])), 4)}
    rows = load_run(f"{level}-test")
    conf = np.array([r["conf"]["account_id"] for r in rows])
    ok = correct(rows, "account_id")
    out["fields"]["account_id"] = {"temperature": None, "before": {
        "acc": float(ok.mean()), "ece": calibrate.ece(conf, ok),
        "reliability": calibrate.reliability(conf, ok)}, "after": None,
        "note": "sequence probability of the extracted value, not rescaled"}
    verbal = RUNS / f"verbal-{level}.jsonl"
    if verbal.exists():
        v = data.read_jsonl(verbal)
        out["verbalized"] = {"asked": len(v), "gave_a_number": int(sum(r["verbalized"] is not None for r in v)),
                             "schema_valid": int(sum(r["schema_valid"] for r in v))}
    return out


def _ticket_conf(items, temps):
    """Ticket confidence is the weaker of the two calibrated field confidences."""
    confs = []
    for logits, pred in items:
        c = []
        for f, options in (("category", data.CATEGORIES), ("priority", data.PRIORITIES)):
            p = calibrate.softmax(np.array([logits[f]]), temps[f])[0]
            c.append(float(p[options.index(pred[f])]) if pred[f] in options else 0.0)
        confs.append(min(c))
    return np.array(confs)


def _items(rows):
    return [(r["logits"], r["modes"]["native"]["pred"]) for r in rows]


def cascade_result(level):
    cfg = yaml.safe_load(open(ROOT / "configs/cascade.yaml", encoding="utf-8"))
    tcfg = label.load_config()
    temps = temperatures(level)
    vgold = val_gold()
    val = [r for r in load_run(f"{level}-val") if vgold.get(r["id"])]
    val_conf = _ticket_conf(_items(val), temps)
    val_ok = correct(val, "category", gold=vgold) & correct(val, "priority", gold=vgold)
    threshold = cascade.choose_threshold(val_conf, val_ok, cfg["target_kept_accuracy"])

    test = load_run(f"{level}-test")
    teacher = {r["id"]: r for r in data.read_jsonl(ROOT / "data/test_teacher_2026.jsonl")}
    conf = _ticket_conf(_items(test), temps)
    per_ticket = np.mean([label.cost_usd(t["tokens_in"], t["tokens_out"], tcfg) for t in teacher.values()])
    fields = {}
    for f in ("category", "priority"):
        fields[f] = (correct(test, f), np.array([(teacher[r["id"]]["label"] or {}).get(f) == r["gold"][f] for r in test], int))
    both_s = fields["category"][0] & fields["priority"][0]
    both_t = fields["category"][1] & fields["priority"][1]
    curve = []
    for t in cascade.THRESHOLDS + [threshold]:
        point = cascade.apply(conf, both_s, both_t, t)
        for f in ("category", "priority"):
            point[f"{f}_acc"] = cascade.apply(conf, *fields[f], t)["acc"]
        point["cost_per_1000"] = cascade.cost_per_1000(point["escalated"], per_ticket)
        curve.append(point)
    chosen = curve[-1]
    curve = sorted({p["threshold"]: p for p in curve}.values(), key=lambda p: p["threshold"])
    teacher_only = {"category_acc": float(fields["category"][1].mean()), "priority_acc": float(fields["priority"][1].mean()),
                    "acc": float(both_t.mean()), "cost_per_1000": 1000 * per_ticket}
    return {
        "level": level, "rule": cfg, "threshold": threshold, "temperatures": {k: round(v, 3) for k, v in temps.items()},
        "teacher": {"model_requested": tcfg["model"], "served": sorted({t["served_model"] for t in teacher.values()}),
                    "cost_per_ticket_usd": per_ticket, "prices": {k: tcfg[k] for k in ("price_input_per_m", "price_output_per_m")}},
        "student_only": {"category_acc": float(fields["category"][0].mean()), "priority_acc": float(fields["priority"][0].mean()),
                         "acc": float(both_s.mean()), "cost_per_1000": 0.0},
        "teacher_only": teacher_only,
        "chosen": chosen,
        "retained_vs_teacher": chosen["acc"] / teacher_only["acc"],
        "cost_fraction_vs_teacher": chosen["escalated"],
        "val_kept_accuracy_at_threshold": float(val_ok[val_conf >= threshold].mean()),
        "curve": curve,
    }


def quantization():
    cfg = yaml.safe_load(open(ROOT / "configs/cascade.yaml", encoding="utf-8"))
    mcfg = yaml.safe_load(open(ROOT / "configs/models.yaml", encoding="utf-8"))
    bench = json.loads((RUNS / "bench.json").read_text()) if (RUNS / "bench.json").exists() else {}
    ref = load_run("q8_0-test")
    rows_out = {}
    for level in LEVELS + ["base-q8_0"]:
        run = f"{level}-test"
        if not (RUNS / f"{run}.jsonl").exists():
            continue
        rows = load_run(run)
        block = {f: stats.summarise(correct(rows, f)) for f in data.FIELDS}
        block["size_mb"] = mcfg["models"][level]["size_mb"]
        block["agrees_with_q8_0"] = round(float(np.mean([a["modes"]["native"]["pred"] == b["modes"]["native"]["pred"]
                                                         for a, b in zip(rows, ref)])), 4)
        block["priority_vs_q8_0_p"] = stats.mcnemar(correct(rows, "priority"), correct(ref, "priority"))
        if "logits" in rows[0]:
            logits = np.array([r["logits"]["priority"] for r in rows])
            y = np.array([data.PRIORITIES.index(r["gold"]["priority"]) for r in rows])
            block["priority_ece"] = calibrate.field_metrics(logits, y, 1.0)["ece"]
        block["latency_ms"] = bench.get(level)
        leak = RUNS / f"leak-{level}.jsonl"
        if leak.exists():
            lr = data.read_jsonl(leak)
            for split in ("train", "test"):
                s = [r for r in lr if r["split"] == split]
                block[f"leak_completion_{split}"] = {"hits": int(sum(r["leak_completion"] for r in s)), "n": len(s)}
                block[f"leak_task_{split}"] = {"hits": int(sum(r["leak_task"] for r in s)), "n": len(s)}
        rows_out[level] = block

    ref_level = rows_out.get("f16")
    chosen, reason = None, None
    if ref_level:
        for level in sorted(LEVELS, key=lambda lv: rows_out.get(lv, {}).get("size_mb") or 1e9):
            b = rows_out.get(level)
            if not b:
                continue
            drop = max(ref_level[f]["acc"] - b[f]["acc"] for f in ("category", "priority"))
            leak_ok = all(b.get(f"leak_{k}_train", {"hits": 0})["hits"] <= b.get(f"leak_{k}_test", {"hits": 0})["hits"]
                          for k in ("completion", "task"))
            if drop <= cfg["quant_max_drop_points"] and leak_ok:
                chosen = level
                reason = (f"smallest file within {cfg['quant_max_drop_points']} point of F16 on category and "
                          f"priority (largest drop {drop:.1f}) with no more training-set leaks than the test control")
                break
    return {"levels": rows_out, "chosen": chosen, "reason": reason,
            "note": "The F16 master was not kept after the v1 Kaggle run. F16, Q6_K and Q4_K_M are "
                    "requantized from the Q8_0 file, so they carry Q8_0 rounding plus their own."}


def trust():
    out = {}
    for model, run in (("base", "base-q8_0"), ("tuned", "q8_0")):
        path = RUNS / f"trust-{run}.jsonl"
        if not path.exists():
            continue
        rows = data.read_jsonl(path)
        ref = {r["id"]: r for r in load_run(f"{run}-test")}
        temps = temperatures("q8_0") if model == "tuned" else {"category": 1.0, "priority": 1.0}
        cas = json.loads((RESULTS / "cascade.json").read_text()) if (RESULTS / "cascade.json").exists() else {}
        thr = cas.get("threshold", 0.5)
        b = {}
        off = [r for r in rows if r["suite"] == "off_task"]
        b["off_task"] = {"n": len(off), "schema_valid": sum(r["schema_valid"] for r in off),
                         "refused": sum(r["refusal"] for r in off),
                         "mean_priority_conf": float(np.mean([r["conf"]["priority"] for r in off]))}
        inj = [r for r in rows if r["suite"] == "injection"]
        b["injection"] = {"n": len(inj), "high_with_injection": sum(r["pred"]["priority"] == "high" for r in inj),
                          "high_without": sum(ref[r["id"]]["modes"]["native"]["pred"]["priority"] == "high" for r in inj)}
        for suite in ("typo", "paraphrase"):
            s = [r for r in rows if r["suite"] == suite]
            orig = [ref[r["id"]] for r in s]
            b[suite] = {"n": len(s)}
            for f in ("category", "priority"):
                b[suite][f"{f}_acc"] = float(np.mean([r["pred"][f] == r["gold"][f] for r in s]))
                b[suite][f"{f}_acc_original"] = float(np.mean([o["modes"]["native"]["pred"][f] == o["gold"][f] for o in orig]))
                b[suite][f"{f}_same_answer"] = float(np.mean([r["pred"][f] == o["modes"]["native"]["pred"][f] for r, o in zip(s, orig)]))
        pii = [r for r in rows if r["suite"] == "pii"]
        b["pii"] = {"n": len(pii), "echoed_any": sum(bool(r["pii"]) for r in pii),
                    "pii_in_account_id": sum(bool(r["pred"]["account_id"]) and bool(set(r["pii"]) - {"email"})
                                             and r["pred"]["account_id"] != r["gold"]["account_id"] for r in pii)}
        if model == "tuned":
            conf = _ticket_conf([(r["logits"], r["pred"]) for r in off], temps)
            b["off_task"]["would_skip_teacher"] = int((conf >= thr).sum())
            b["off_task"]["threshold"] = thr
        out[model] = b
    return out


def geometry(level="q8_0"):
    """Accuracy and confidence by how mixed each ticket's neighbourhood is."""
    geo = {g["id"]: g for g in json.loads((RUNS / f"geometry-{level}.json").read_text(encoding="utf-8"))}
    rows = load_run(f"{level}-test")
    purity = np.array([geo[r["id"]]["purity"] for r in rows])
    ok = correct(rows, "priority")
    conf = np.array([r["conf"]["priority"] for r in rows])
    groups = []
    for name, lo, hi in (("mixed, under 0.5", 0.0, 0.5), ("partly mixed, 0.5 to 0.8", 0.5, 0.8), ("clean, 0.8 and up", 0.8, 1.01)):
        m = (purity >= lo) & (purity < hi)
        groups.append({"neighbourhood": name, "n": int(m.sum()), "priority_acc": float(ok[m].mean()),
                       "mean_confidence": float(conf[m].mean())})
    return {"level": level, "k": 10, "groups": groups,
            "corr_purity_confidence": float(np.corrcoef(purity, conf)[0, 1])}


def build():
    RESULTS.mkdir(parents=True, exist_ok=True)
    mcfg = yaml.safe_load(open(ROOT / "configs/models.yaml", encoding="utf-8"))
    deployed = mcfg["deployed"]
    outputs = {"headline": headline, "decoding": decoding,
               "calibration": lambda: calibration(deployed),
               "cascade": lambda: cascade_result(deployed),
               "quantization": quantization, "trust": trust, "geometry": geometry}
    for name, fn in outputs.items():
        (RESULTS / f"{name}.json").write_text(json.dumps(fn(), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print("wrote", name)


if __name__ == "__main__":
    build()
