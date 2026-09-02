PY ?= python
LEVELS = f16 q6_k q4_k_m

.PHONY: pipeline label train export runs eval check serve test

# Raw tickets to result tables. Training needs a GPU and the `train` extra.
pipeline: label train export runs eval

label:
	$(PY) -m triage.data
	$(PY) -m triage.label

train:
	$(PY) -m triage.train

export:
	$(PY) -m triage.export merge out/lora --gguf models/triage-0.6b-f16.gguf
	$(PY) -m triage.export quantize --src models/triage-0.6b-f16.gguf q8_0 q6_k q4_k_m

runs:
	$(PY) -m triage.export fetch base-q8_0 q8_0 $(LEVELS)
	$(PY) -m triage.infer --model q8_0 --modes native,outlines,xgrammar
	$(PY) -m triage.infer --model base-q8_0 --modes native,outlines,xgrammar
	for m in $(LEVELS); do $(PY) -m triage.infer --model $$m; done
	for m in q8_0 $(LEVELS); do $(PY) -m triage.infer --model $$m --split val; done
	for m in q8_0 base-q8_0; do $(PY) -m triage.trust suite --model $$m; done
	for m in base-q8_0 q8_0 $(LEVELS); do $(PY) -m triage.trust leak --model $$m; done
	$(PY) -m triage.calibrate
	$(PY) -m triage.export bench
	$(PY) -m triage.figures

eval:
	$(PY) -m triage.eval
	$(PY) -m triage.readme

check:
	$(PY) -m triage.export fetch q8_0
	$(PY) -m triage.check -n 40

serve:
	$(PY) -m uvicorn service.app:app --port 8000

test:
	$(PY) -m pytest -q
