"""Accuracy with bootstrap intervals and exact McNemar tests on paired predictions."""
import math
import re

import numpy as np

B = 10_000
SEED = 20260926


def bootstrap_ci(x, level=0.95, n=B, seed=SEED):
    x = np.asarray(x, dtype=float)
    idx = np.random.default_rng(seed).integers(0, len(x), size=(n, len(x)))
    means = x[idx].mean(axis=1)
    a = (1 - level) / 2
    return float(np.quantile(means, a)), float(np.quantile(means, 1 - a))


def paired_diff_ci(a, b, level=0.95, n=B, seed=SEED):
    # Resample tickets, not predictions, so each model keeps its answer to the same email.
    return bootstrap_ci(np.asarray(a, float) - np.asarray(b, float), level, n, seed)


def mcnemar(a, b):
    """Exact two-sided McNemar p-value from the discordant pairs."""
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    only_a, only_b = int((a & ~b).sum()), int((~a & b).sum())
    n = only_a + only_b
    if n == 0:
        return 1.0
    k = min(only_a, only_b)
    # Sum the binomial tail in log space. With 600 discordant pairs 2**n overflows a float.
    logs = [math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) - n * math.log(2)
            for i in range(k + 1)]
    top = max(logs)
    tail = math.exp(top) * sum(math.exp(v - top) for v in logs)
    return min(1.0, 2 * tail)


def summarise(correct):
    lo, hi = bootstrap_ci(correct)
    return {"acc": round(100 * float(np.mean(correct)), 1),
            "ci": [round(100 * lo, 1), round(100 * hi, 1)], "n": int(len(correct))}


def parse_v1(path):
    """Read the numbers v1 printed in its eval cell, so the README can show both."""
    text = open(path, encoding="utf-8").read()
    out = {"baseline_priority": float(re.search(r"always 'high'\): ([\d.]+)%", text).group(1))}
    for name, key in (("BASE", "base"), ("FINE-TUNED", "tuned")):
        block = text.split(f"===== {name} =====")[1]
        m = re.search(r"\(([\d.]+)%\) \| priority ([\d.]+)% \| category ([\d.]+)%", block)
        out[f"{key}_valid_json"] = float(m.group(1))
        out[f"{key}_priority"] = float(m.group(2))
        out[f"{key}_category"] = float(m.group(3))
    return out
