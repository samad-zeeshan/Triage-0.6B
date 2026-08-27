"""Temperature scaling and the calibration metrics reported beside every accuracy.

Confidence is the model's own probability for each allowed label, read from teacher-forced scoring in infer.py."""
import numpy as np


def softmax(logits, t=1.0):
    z = np.asarray(logits, float) / t
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def nll(logits, y, t):
    p = softmax(logits, t)[np.arange(len(y)), y]
    return float(-np.log(np.clip(p, 1e-12, 1)).mean())


def fit_temperature(logits, y):
    """One scalar T minimising validation NLL, by golden-section search on log T.

    A grid plus golden section avoids pulling in an optimiser for a single parameter."""
    lo, hi = np.log(0.05), np.log(20.0)
    grid = np.linspace(lo, hi, 60)
    best = grid[int(np.argmin([nll(logits, y, np.exp(g)) for g in grid]))]
    a, b = best - 0.2, best + 0.2
    ratio = (np.sqrt(5) - 1) / 2
    for _ in range(60):
        c, d = b - ratio * (b - a), a + ratio * (b - a)
        if nll(logits, y, np.exp(c)) < nll(logits, y, np.exp(d)):
            b = d
        else:
            a = c
    return float(np.exp((a + b) / 2))


def ece(conf, correct, n_bins=15):
    conf, correct = np.asarray(conf, float), np.asarray(correct, float)
    edges = np.linspace(0, 1, n_bins + 1)
    idx = np.clip(np.digitize(conf, edges[1:-1], right=True), 0, n_bins - 1)
    total = 0.0
    for b in range(n_bins):
        m = idx == b
        if m.any():
            total += m.mean() * abs(conf[m].mean() - correct[m].mean())
    return float(total)


def brier(probs, y):
    probs = np.asarray(probs, float)
    onehot = np.eye(probs.shape[1])[y]
    return float(((probs - onehot) ** 2).sum(axis=1).mean())


def reliability(conf, correct, n_bins=10):
    conf, correct = np.asarray(conf, float), np.asarray(correct, float)
    edges = np.linspace(0, 1, n_bins + 1)
    idx = np.clip(np.digitize(conf, edges[1:-1], right=True), 0, n_bins - 1)
    out = []
    for b in range(n_bins):
        m = idx == b
        out.append({"lo": float(edges[b]), "hi": float(edges[b + 1]), "n": int(m.sum()),
                    "conf": float(conf[m].mean()) if m.any() else None,
                    "acc": float(correct[m].mean()) if m.any() else None})
    return out


def field_metrics(logits, y, t):
    """Metrics for the argmax readout of the scored distribution at temperature t."""
    p = softmax(logits, t)
    pred = p.argmax(axis=1)
    conf = p.max(axis=1)
    correct = (pred == y).astype(float)
    return {"t": round(float(t), 4), "acc": float(correct.mean()), "ece": ece(conf, correct),
            "brier": brier(p, y), "nll": nll(logits, y, t),
            "reliability": reliability(conf, correct)}
