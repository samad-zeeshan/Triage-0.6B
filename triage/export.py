"""Fetch, merge, convert and quantize the model files, and time each quantization level.

Conversion needs a llama.cpp checkout (LLAMA_CPP_DIR) for convert_hf_to_gguf.py and llama-quantize."""
import hashlib
import json
import os
import statistics
import subprocess
import sys
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
QUANT_TYPES = {"f16": "F16", "q8_0": "Q8_0", "q6_k": "Q6_K", "q4_k_m": "Q4_K_M"}


def _cfg():
    return yaml.safe_load(open(ROOT / "configs/models.yaml", encoding="utf-8"))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(name):
    cfg = _cfg()
    spec = cfg["models"][name]
    out = ROOT / "models" / spec["file"]
    if not out.exists():
        out.parent.mkdir(exist_ok=True)
        url = spec.get("url") or f"{cfg['release']}/{spec['file']}"
        print("downloading", url)
        try:
            urllib.request.urlretrieve(url, out)
        except OSError:
            if "from" not in spec:
                raise
            # Not published on its own, so rebuild it from its source file.
            return quantize(fetch(spec["from"]), name)
    if spec.get("sha256") and sha256(out) != spec["sha256"]:
        raise RuntimeError(f"{out.name} does not match the sha256 in configs/models.yaml")
    return out


def _llama_tool(name):
    base = Path(os.environ.get("LLAMA_CPP_DIR", ROOT / ".cache/llama"))
    for candidate in (base / f"{name}.exe", base / name, base / "build/bin" / name):
        if candidate.exists():
            return candidate
    raise RuntimeError(f"{name} not found, set LLAMA_CPP_DIR to a llama.cpp build")


def quantize(src, level):
    out = ROOT / "models" / _cfg()["models"][level]["file"]
    # Requantizing an already quantized file stacks rounding errors, so llama-quantize
    # refuses unless told. v2 has to, because the F16 master was not kept.
    subprocess.run([str(_llama_tool("llama-quantize")), "--allow-requantize", str(src), str(out),
                    QUANT_TYPES[level]], check=True)
    return out


def merge(adapter_dir, out_dir, base="Qwen/Qwen3-0.6B"):
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer
    model = PeftModel.from_pretrained(AutoModelForCausalLM.from_pretrained(base), adapter_dir)
    model = model.merge_and_unload().half()
    model.save_pretrained(out_dir, safe_serialization=True)
    AutoTokenizer.from_pretrained(base).save_pretrained(out_dir)
    return Path(out_dir)


def to_gguf(merged_dir, out_file, outtype="f16"):
    script = Path(os.environ.get("LLAMA_CPP_DIR", ROOT / ".cache/llama.cpp")) / "convert_hf_to_gguf.py"
    subprocess.run([sys.executable, str(script), str(merged_dir), "--outfile", str(out_file),
                    "--outtype", outtype], check=True)
    return Path(out_file)


def bench(levels=("f16", "q8_0", "q6_k", "q4_k_m", "base-q8_0"), n=50, threads=6):
    """Median milliseconds for one ticket, prompt plus native JSON, on this CPU."""
    from triage import data, infer
    rows = data.load_chat(ROOT / "data/test_chat.jsonl")[:n]
    out = {}
    for level in levels:
        engine = infer.Engine(infer.model_path(level), n_threads=threads)
        engine.predict(rows[0]["email"], score=False)
        times = []
        for r in rows:
            res = engine.predict(r["email"], score=False)
            times.append(1000 * (res["prompt_s"] + res["modes"]["native"]["gen_s"]))
        out[level] = round(statistics.median(times), 1)
        print(level, out[level], "ms")
    out["threads"] = threads
    (ROOT / "eval/runs/bench.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    return out


def main():
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("names", nargs="*", default=["q8_0"])
    q = sub.add_parser("quantize")
    q.add_argument("--src", default=None)
    q.add_argument("levels", nargs="*", default=["f16", "q6_k", "q4_k_m"])
    m = sub.add_parser("merge")
    m.add_argument("adapter")
    m.add_argument("--out", default="out/merged")
    m.add_argument("--gguf", default="models/triage-0.6b-f16.gguf")
    sub.add_parser("bench")
    a = p.parse_args()
    if a.cmd == "fetch":
        for name in a.names:
            print(fetch(name))
    elif a.cmd == "quantize":
        src = a.src or ROOT / "models" / _cfg()["models"]["q8_0"]["file"]
        for level in a.levels:
            print(quantize(src, level))
    elif a.cmd == "merge":
        to_gguf(merge(a.adapter, a.out), a.gguf)
    else:
        bench()


if __name__ == "__main__":
    main()
