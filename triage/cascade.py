"""Small model first, teacher when unsure: threshold sweep, cost and operating point."""
import numpy as np

THRESHOLDS = [round(x, 3) for x in np.concatenate([np.linspace(0, 0.9, 19), np.linspace(0.91, 1.0, 10)])]


def apply(conf, student_correct, teacher_correct, threshold):
    conf = np.asarray(conf, float)
    s, t = np.asarray(student_correct, bool), np.asarray(teacher_correct, bool)
    up = conf < threshold
    final = np.where(up, t, s)
    return {"threshold": float(threshold), "escalated": float(up.mean()), "acc": float(final.mean()),
            "kept_acc": float(s[~up].mean()) if (~up).any() else None}


def sweep(conf, student_correct, teacher_correct, thresholds=THRESHOLDS):
    return [apply(conf, student_correct, teacher_correct, t) for t in thresholds]


def choose_threshold(conf, correct, target=0.95):
    """Lowest threshold whose accepted answers are at least `target` correct.

    Picked on validation only. It does not need teacher answers, which matters because on
    validation the teacher's answer is the gold label and would look perfect."""
    conf, correct = np.asarray(conf, float), np.asarray(correct, bool)
    for t in np.round(np.arange(0, 1.0001, 0.005), 3):
        kept = conf >= t
        if kept.any() and correct[kept].mean() >= target:
            return float(t)
    return 1.0


def cost_per_1000(escalated, teacher_cost_per_ticket):
    return 1000 * escalated * teacher_cost_per_ticket
