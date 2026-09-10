"""Run a Triage GGUF on one email and return triage JSON with a confidence per field.

Decoding is a hand-written greedy loop so native, Outlines and XGrammar modes share one prompt pass on the same weights."""
import json
import time
from functools import lru_cache
from pathlib import Path

import numpy as np
import outlines_core as oc
import xgrammar as xgr
from llama_cpp import Llama

from triage import data

MODES = ["native", "outlines", "xgrammar"]
IM_END, END_OF_TEXT = 151645, 151643


def _bits(bitmask, n_vocab):
    return np.unpackbits(bitmask.view(np.uint8), bitorder="little")[:n_vocab].astype(bool)


def _log_softmax(x):
    x = x - x.max()
    return x - np.log(np.exp(x).sum())


class _XGrammar:
    def __init__(self, compiled, n_vocab):
        self.matcher = xgr.GrammarMatcher(compiled)
        self.n_vocab = n_vocab
        self.buf = np.full(xgr.get_bitmask_shape(1, n_vocab), -1, dtype=np.int32)

    def allowed(self):
        self.matcher.fill_next_token_bitmask(self.buf)
        return _bits(self.buf, self.n_vocab)

    def advance(self, token):
        self.matcher.accept_token(token)


class _Outlines:
    def __init__(self, index, n_vocab):
        self.guide = oc.Guide(index)
        self.n_vocab = n_vocab
        self.buf = np.zeros(xgr.get_bitmask_shape(1, n_vocab), dtype=np.int32)

    def allowed(self):
        self.buf[:] = 0
        self.guide.write_mask_into(self.buf.ctypes.data, self.buf.size, 4)
        return _bits(self.buf, self.n_vocab)

    def advance(self, token):
        self.guide.advance(token)


@lru_cache(maxsize=2)
def _grammars(vocab):
    """Compile the schema once per vocabulary. Both libraries take a few hundred ms."""
    n = len(vocab)
    schema = json.dumps(data.SCHEMA)
    info = xgr.TokenizerInfo(list(vocab), vocab_type=xgr.VocabType.RAW, vocab_size=n,
                             stop_token_ids=[IM_END], add_prefix_space=False)
    xgr_compiled = xgr.GrammarCompiler(info).compile_json_schema(schema, any_whitespace=True)
    by_bytes = {}
    for i, piece in enumerate(vocab):
        # Control tokens detokenize to nothing. Outlines rejects empty strings, and
        # neither library should ever emit them inside JSON anyway.
        if piece and i != IM_END:
            by_bytes.setdefault(piece, []).append(i)
    index = oc.Index(oc.json_schema.build_regex_from_schema(schema),
                     oc.Vocabulary(IM_END, by_bytes))
    return xgr_compiled, index


class Engine:
    def __init__(self, path, n_threads=8, n_ctx=2048, max_tokens=80):
        self.path = Path(path)
        self.llm = Llama(model_path=str(path), n_ctx=n_ctx, n_threads=n_threads,
                         n_threads_batch=n_threads, n_gpu_layers=0, seed=0, verbose=False)
        self.n_vocab = self.llm.n_vocab()
        self.max_tokens = max_tokens
        self._vocab = tuple(self.llm.detokenize([i]) for i in range(self.n_vocab))

    def tokenize(self, text, special=False):
        return self.llm.tokenize(text.encode("utf-8"), add_bos=False, special=special)

    def _logits(self):
        # llama-cpp-python stopped filling llm.scores unless logits_all is set, which
        # costs n_ctx x vocab floats. Reading the context buffer gives the last row only.
        return np.ctypeslib.as_array(self.llm._ctx.get_logits(), shape=(self.n_vocab,)).copy()

    def _rewind(self, n):
        self.llm.n_tokens = n

    def _constraint(self, mode):
        if mode == "native":
            return None
        xgr_compiled, index = _grammars(self._vocab)
        if mode == "xgrammar":
            return _XGrammar(xgr_compiled, self.n_vocab)
        return _Outlines(index, self.n_vocab)

    def _generate(self, n_prompt, first_logits, mode):
        self._rewind(n_prompt)
        constraint = self._constraint(mode)
        logits, out = first_logits, []
        for _ in range(self.max_tokens):
            if constraint is not None:
                logits = np.where(constraint.allowed(), logits, -np.inf)
            token = int(np.argmax(logits))
            if token in (IM_END, END_OF_TEXT):
                break
            if constraint is not None:
                constraint.advance(token)
            out.append(token)
            self.llm.eval([token])
            logits = self._logits()
        return self.llm.detokenize(out).decode("utf-8", errors="replace"), len(out)

    def _seq_logprobs(self, prompt_tokens, texts):
        """Teacher-forced log-probability of each candidate continuation after the prompt."""
        seqs = [self.tokenize(t) for t in texts]
        shared = 0
        while all(len(s) > shared and s[shared] == seqs[0][shared] for s in seqs):
            shared += 1
        # Re-evaluate the last prompt token so its logits are back in the buffer.
        self._rewind(len(prompt_tokens) - 1)
        self.llm.eval([prompt_tokens[-1]] + seqs[0][:shared])
        base_n, base_logits = self.llm.n_tokens, self._logits()
        scores = []
        for seq in seqs:
            self._rewind(base_n)
            logits, total = base_logits, 0.0
            rest = seq[shared:]
            for j, token in enumerate(rest):
                total += float(_log_softmax(logits)[token])
                if j < len(rest) - 1:
                    self.llm.eval([token])
                    logits = self._logits()
            scores.append(total)
        return np.array(scores)

    def _score(self, prompt_tokens, pred):
        logp = {}
        head = '{"category": "'
        logp["category"] = self._seq_logprobs(prompt_tokens, [head + c + '",' for c in data.CATEGORIES])
        cat = pred["category"]
        if cat not in data.CATEGORIES:
            cat = data.CATEGORIES[int(np.argmax(logp["category"]))]
        head = f'{{"category": "{cat}", "priority": "'
        logp["priority"] = self._seq_logprobs(prompt_tokens, [head + p + '",' for p in data.PRIORITIES])
        pri = pred["priority"]
        if pri not in data.PRIORITIES:
            pri = data.PRIORITIES[int(np.argmax(logp["priority"]))]
        head = f'{{"category": "{cat}", "priority": "{pri}", "account_id":'
        acct = pred["account_id"]
        value = " null}" if acct is None else " " + json.dumps(acct) + "}"
        # The second candidate only exists so the shared-prefix logic has something to
        # diverge from. Its score is thrown away.
        acct_lp = float(self._seq_logprobs(prompt_tokens, [head + value, head + " @"])[0])
        probs, conf = {}, {}
        for field, options in (("category", data.CATEGORIES), ("priority", data.PRIORITIES)):
            p = np.exp(_log_softmax(logp[field]))
            probs[field] = {o: float(v) for o, v in zip(options, p)}
            conf[field] = probs[field].get(pred[field], 0.0)
        conf["account_id"] = float(np.exp(acct_lp))
        logits = {f: [float(v) for v in logp[f]] for f in ("category", "priority")}
        return probs, conf, logits

    def predict(self, email, modes=("native",), score=True, system=data.SYSTEM):
        t0 = time.perf_counter()
        prompt_tokens = self.tokenize(data.prompt(email, system), special=True)
        self.llm.reset()
        self.llm.eval(prompt_tokens)
        first = self._logits()
        result = {"n_prompt": len(prompt_tokens), "prompt_s": time.perf_counter() - t0, "modes": {}}
        for mode in modes:
            t1 = time.perf_counter()
            raw, n_gen = self._generate(len(prompt_tokens), first, mode)
            parsed = data.parse_output(raw)
            result["modes"][mode] = {"raw": raw, "json_valid": parsed["json_valid"],
                                     "schema_valid": parsed["schema_valid"], "pred": parsed["fields"],
                                     "n_gen": n_gen, "gen_s": time.perf_counter() - t1}
        main = result["modes"][modes[0]]
        result.update({k: main[k] for k in ("raw", "json_valid", "schema_valid", "pred")})
        if score:
            t2 = time.perf_counter()
            result["probs"], result["conf"], result["logits"] = self._score(prompt_tokens, main["pred"])
            result["score_s"] = time.perf_counter() - t2
        return result

    def complete(self, text, max_tokens=12):
        """Plain greedy continuation with no chat template, for the leakage probe."""
        tokens = self.tokenize(text)
        self.llm.reset()
        self.llm.eval(tokens)
        out = []
        for _ in range(max_tokens):
            token = int(np.argmax(self._logits()))
            if token in (IM_END, END_OF_TEXT):
                break
            out.append(token)
            self.llm.eval([token])
        return self.llm.detokenize(out).decode("utf-8", errors="replace")


def model_path(name, root=Path(__file__).resolve().parents[1]):
    import yaml
    cfg = yaml.safe_load(open(root / "configs/models.yaml", encoding="utf-8"))
    path = root / "models" / cfg["models"][name]["file"]
    if not path.exists():
        raise FileNotFoundError(f"{path} is missing. The model file is not in the repository, "
                                f"fetch it with `python -m triage.export fetch {name}`.")
    return path


def _compact(result, row):
    rnd = lambda x: round(x, 6)
    rec = {"id": row["id"], "gold": row.get("gold"), "n_prompt": result["n_prompt"],
           "prompt_ms": round(1000 * result["prompt_s"], 1), "modes": {}}
    for mode, m in result["modes"].items():
        rec["modes"][mode] = {"raw": m["raw"], "json_valid": m["json_valid"],
                              "schema_valid": m["schema_valid"], "pred": m["pred"],
                              "n_gen": m["n_gen"], "gen_ms": round(1000 * m["gen_s"], 1)}
    if "probs" in result:
        rec["probs"] = {f: {k: rnd(v) for k, v in p.items()} for f, p in result["probs"].items()}
        rec["conf"] = {f: rnd(v) for f, v in result["conf"].items()}
        rec["logits"] = {f: [rnd(v) for v in lv] for f, lv in result["logits"].items()}
        rec["score_ms"] = round(1000 * result["score_s"], 1)
    return rec


def run(model, rows, out, modes=("native",), score=True, threads=8, limit=None):
    """Predict every row and append to a JSONL file, skipping ids already there."""
    out = Path(out)
    done = {r["id"] for r in data.read_jsonl(out)} if out.exists() else set()
    todo = [r for r in rows[:limit] if r["id"] not in done]
    if not todo:
        return out
    engine = Engine(model_path(model), n_threads=threads)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "a", encoding="utf-8", newline="\n") as f:
        for i, row in enumerate(todo):
            rec = _compact(engine.predict(row["email"], modes=modes, score=score), row)
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            if i % 50 == 0:
                print(f"{out.name}: {len(done) + i + 1}/{len(rows[:limit])}", flush=True)
    return out


SPLITS = {"test": "data/test_chat.jsonl", "val": "data/val_emails.jsonl"}


def main():
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", default="q8_0")
    p.add_argument("--split", default="test", choices=list(SPLITS))
    p.add_argument("--modes", default="native")
    p.add_argument("--no-score", action="store_true")
    p.add_argument("--threads", type=int, default=8)
    p.add_argument("--limit", type=int)
    p.add_argument("--out")
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    path = root / SPLITS[a.split]
    rows = data.load_chat(path) if a.split == "test" else data.read_jsonl(path)
    out = a.out or root / f"eval/runs/{a.model}-{a.split}.jsonl"
    run(a.model, rows, out, modes=tuple(a.modes.split(",")), score=not a.no_score,
        threads=a.threads, limit=a.limit)


if __name__ == "__main__":
    main()
