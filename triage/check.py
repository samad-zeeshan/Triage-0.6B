"""CI check: rerun the committed GGUF on a CPU-sized slice and compare with the recorded full run.

Different CPUs round floats differently, so a rare flipped argmax is allowed, a pattern of them is not."""
import argparse
import sys
from pathlib import Path

from triage import data, infer

ROOT = Path(__file__).resolve().parents[1]


def check(n=40, min_agreement=0.95, threads=4):
    rows = data.load_chat(ROOT / "data/test_chat.jsonl")[:n]
    recorded = {r["id"]: r for r in data.read_jsonl(ROOT / "eval/runs/q8_0-test.jsonl")}
    engine = infer.Engine(infer.model_path("q8_0"), n_threads=threads)
    same, schema_ok, hits = 0, 0, 0
    for row in rows:
        out = engine.predict(row["email"], modes=infer.MODES, score=False)
        ref = recorded[row["id"]]["modes"]
        same += all(out["modes"][m]["pred"] == ref[m]["pred"] for m in infer.MODES)
        schema_ok += all(out["modes"][m]["schema_valid"] for m in ("outlines", "xgrammar"))
        hits += out["pred"]["priority"] == row["gold"]["priority"]
    agreement = same / n
    print(f"subset {n}: agreement with recorded run {agreement:.3f}, "
          f"constrained schema valid {schema_ok}/{n}, priority accuracy {hits / n:.3f}")
    return agreement >= min_agreement and schema_ok == n


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("-n", type=int, default=40)
    a = p.parse_args()
    sys.exit(0 if check(a.n) else 1)
