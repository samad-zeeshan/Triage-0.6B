"""Draw the SVG figures in eval/figures from the result files, and compute the ticket embeddings.

Embedding is the only step that runs the model. It stores 2D coordinates and neighbour purity, not the vectors."""
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "eval/figures"
RESULTS = ROOT / "eval/results"

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK_2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


def embed(level="q8_0", k=10, threads=6):
    """Mean-pooled last-layer embedding of each test email, projected to 2D with PCA."""
    from llama_cpp import Llama

    from triage import data, infer
    rows = data.load_chat(ROOT / "data/test_chat.jsonl")
    llm = Llama(model_path=str(infer.model_path(level)), embedding=True, pooling_type=1,
                n_ctx=2048, n_threads=threads, n_gpu_layers=0, verbose=False)
    vecs = np.array([llm.create_embedding(r["email"])["data"][0]["embedding"] for r in rows], dtype=np.float32)
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
    centred = vecs - vecs.mean(0)
    _, _, vt = np.linalg.svd(centred, full_matrices=False)
    xy = centred @ vt[:2].T
    sims = vecs @ vecs.T
    np.fill_diagonal(sims, -np.inf)
    nn = np.argsort(-sims, axis=1)[:, :k]
    gold = np.array([r["gold"]["priority"] for r in rows])
    # Share of the 10 nearest tickets that carry the same gold priority. Low purity
    # means the email sits where the teacher's labels are mixed.
    purity = (gold[nn] == gold[:, None]).mean(1)
    out = [{"id": r["id"], "x": round(float(a), 5), "y": round(float(b), 5), "purity": round(float(p), 3)}
           for r, (a, b), p in zip(rows, xy, purity)]
    (ROOT / f"eval/runs/geometry-{level}.json").write_text(json.dumps(out) + "\n", encoding="utf-8")
    return out


def _style(plt):
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK_2,
        "xtick.color": INK_2, "ytick.color": INK_2, "axes.facecolor": SURFACE, "figure.facecolor": SURFACE,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.spines.top": False,
        "axes.spines.right": False, "svg.hashsalt": "triage", "legend.frameon": False,
    })


def _save(fig, name):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / name, format="svg", bbox_inches="tight", metadata={"Date": None})
    # Matplotlib writes an RDF block naming itself and its version. It adds nothing a
    # reader sees and makes the file change on every library upgrade.
    path = FIG / name
    text = re.sub(r"\s*<metadata>.*?</metadata>", "", path.read_text(encoding="utf-8"), flags=re.S)
    path.write_text(text, encoding="utf-8")


def reliability(plt):
    cal = json.loads((RESULTS / "calibration.json").read_text(encoding="utf-8"))
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.8), sharey=True)
    for ax, field in zip(axes, ("category", "priority")):
        f = cal["fields"][field]
        ax.plot([0, 1], [0, 1], color=INK_2, linewidth=1, linestyle=(0, (3, 3)))
        for key, color, name in (("before", ORANGE, "raw"), ("after", BLUE, f"T = {f['temperature']}")):
            bins = [b for b in f[key]["reliability"] if b["n"] >= 5]
            ax.plot([b["conf"] for b in bins], [b["acc"] for b in bins], color=color, linewidth=2,
                    marker="o", markersize=5, label=f"{name}, ECE {100 * f[key]['ece']:.1f}")
        ax.set_title(field, color=INK, loc="left")
        ax.set_xlabel("model confidence")
        ax.set_xlim(0.3, 1.0)
        ax.set_ylim(0.3, 1.0)
        ax.legend(loc="upper left")
    axes[0].set_ylabel("share correct on test")
    _save(fig, "reliability.svg")


def cascade_curve(plt):
    cas = json.loads((RESULTS / "cascade.json").read_text(encoding="utf-8"))
    pts = sorted(cas["curve"], key=lambda p: p["escalated"])
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.plot([100 * p["escalated"] for p in pts], [100 * p["acc"] for p in pts], color=BLUE, linewidth=2,
            label="cascade, category and priority both right")
    ch = cas["chosen"]
    ax.scatter([100 * ch["escalated"]], [100 * ch["acc"]], s=70, color=BLUE, edgecolor=SURFACE, linewidth=2, zorder=3)
    ax.annotate(f"chosen: {100 * ch['escalated']:.0f}% escalated, ${ch['cost_per_1000']:.3f} per 1,000",
                (100 * ch["escalated"], 100 * ch["acc"]), xytext=(10, -22), textcoords="offset points", color=INK)
    so, to = cas["student_only"], cas["teacher_only"]
    ax.scatter([0], [100 * so["acc"]], s=60, color=ORANGE, zorder=3, label="small model only")
    ax.scatter([100], [100 * to["acc"]], s=60, color=AQUA, zorder=3, label="teacher only")
    ax.set_xlabel("share of tickets sent to the teacher (%)")
    ax.set_ylabel("accuracy against v1 gold (%)")
    ax.legend(loc="lower right")
    _save(fig, "cascade.svg")


def geometry(plt, level="q8_0"):
    geo = {g["id"]: g for g in json.loads((ROOT / f"eval/runs/geometry-{level}.json").read_text())}
    from triage import data
    runs = {r["id"]: r for r in data.read_jsonl(ROOT / f"eval/runs/{level}-test.jsonl")}
    fig, ax = plt.subplots(figsize=(6.6, 5.0))
    ok = [g for i, g in geo.items() if runs[i]["modes"]["native"]["pred"]["priority"] == runs[i]["gold"]["priority"]]
    bad = [g for i, g in geo.items() if runs[i]["modes"]["native"]["pred"]["priority"] != runs[i]["gold"]["priority"]]
    ax.scatter([g["x"] for g in ok], [g["y"] for g in ok], s=9, color=BLUE, alpha=0.45, linewidth=0, label="priority right")
    ax.scatter([g["x"] for g in bad], [g["y"] for g in bad], s=18, color=ORANGE, linewidth=0, label="priority wrong")
    low = [g for i, g in geo.items() if runs[i]["conf"]["priority"] < 0.8]
    ax.scatter([g["x"] for g in low], [g["y"] for g in low], s=46, facecolor="none", edgecolor=INK,
               linewidth=0.8, label="confidence below 0.8")
    ax.set_xlabel("first principal component")
    ax.set_ylabel("second principal component")
    ax.legend(loc="best")
    _save(fig, "geometry.svg")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "embed":
        embed()
        return
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    _style(plt)
    for fn in (reliability, cascade_curve, geometry):
        fn(plt)
        plt.close("all")
    print("figures written")


if __name__ == "__main__":
    main()
