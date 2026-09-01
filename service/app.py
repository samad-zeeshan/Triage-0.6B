"""HTTP service: one email in, triage JSON out, with calibrated confidence and the escalation decision.

Threshold and temperatures are read from eval/results/cascade.json so the service runs the operating point the tables report."""
import json
import os
import time
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from triage import calibrate, data

ROOT = Path(__file__).resolve().parents[1]


class Ticket(BaseModel):
    email: str


def load_settings():
    cas = json.loads((ROOT / "eval/results/cascade.json").read_text(encoding="utf-8"))
    return {"threshold": cas["threshold"], "temperatures": cas["temperatures"], "level": cas["level"]}


def calibrated(result, temps):
    conf = {}
    for field, options in (("category", data.CATEGORIES), ("priority", data.PRIORITIES)):
        p = calibrate.softmax(np.array([result["logits"][field]]), temps[field])[0]
        pred = result["pred"][field]
        conf[field] = float(p[options.index(pred)]) if pred in options else 0.0
    conf["account_id"] = float(result["conf"]["account_id"])
    return conf


def create_app(engine=None, teacher=None, settings=None):
    app = FastAPI(title="Triage", version="2.0.0")
    state = {"engine": engine, "teacher": teacher, "settings": settings}

    def get_engine():
        # Load lazily so importing the module, and the docs page, never touch the model file.
        if state["engine"] is None:
            from triage import infer
            state["settings"] = state["settings"] or load_settings()
            state["engine"] = infer.Engine(infer.model_path(state["settings"]["level"]),
                                           n_threads=int(os.environ.get("TRIAGE_THREADS", "4")))
        return state["engine"]

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.post("/triage")
    def triage(ticket: Ticket):
        if not ticket.email.strip():
            raise HTTPException(status_code=422, detail="email is empty")
        start = time.perf_counter()
        result = get_engine().predict(ticket.email[:8000])
        settings = state["settings"] or load_settings()
        conf = calibrated(result, settings["temperatures"])
        escalate = min(conf["category"], conf["priority"]) < settings["threshold"]
        body = {"triage": result["pred"], "confidence": conf, "escalate": escalate,
                "threshold": settings["threshold"], "answered_by": "small model",
                "small_model_ms": round(1000 * (time.perf_counter() - start))}
        if escalate:
            if state["teacher"] is None:
                body["answered_by"] = "small model, teacher not configured"
            else:
                answer = state["teacher"].label(ticket.email)
                body.update({"small_model": result["pred"], "triage": answer["label"], "answered_by": "teacher"})
        return body

    return app


def _default_teacher():
    from triage.label import Teacher, load_config
    cfg = load_config()
    return Teacher(cfg, cache=None) if os.environ.get(cfg["key_env"]) else None


app = create_app(teacher=_default_teacher())
