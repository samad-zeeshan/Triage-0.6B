"""LoRA fine-tune of Qwen3-0.6B on the teacher-labelled chat data, driven by configs/train.yaml.

Same recipe as the v1 Kaggle notebook. Needs the `train` extra and ideally a CUDA GPU."""
import argparse
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def collate(batch, pad_id):
    import torch
    width = max(len(b["input_ids"]) for b in batch)
    ids, mask, labels = [], [], []
    for b in batch:
        x = b["input_ids"]
        k = width - len(x)
        ids.append(x + [pad_id] * k)
        mask.append([1] * len(x) + [0] * k)
        # Padding gets -100 so the loss skips it. Prompt tokens are left in, as in v1.
        labels.append(x + [-100] * k)
    return {"input_ids": torch.tensor(ids), "attention_mask": torch.tensor(mask),
            "labels": torch.tensor(labels)}


def train(cfg, max_steps=-1, limit=None):
    import torch
    from datasets import load_dataset
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, set_seed

    set_seed(cfg["seed"])
    tok = AutoTokenizer.from_pretrained(cfg["base_model"])
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(cfg["base_model"])
    model.config.use_cache = False

    ds = load_dataset("json", data_files=str(ROOT / cfg["train_file"]), split="train")
    if limit:
        ds = ds.select(range(limit))
    ds = ds.map(lambda ex: {"text": tok.apply_chat_template(ex["messages"], tokenize=False, enable_thinking=False)},
                remove_columns=["messages"])
    ds = ds.map(lambda ex: tok(ex["text"], truncation=True, max_length=cfg["max_length"], add_special_tokens=False),
                remove_columns=["text"])

    lora = cfg["lora"]
    model = get_peft_model(model, LoraConfig(r=lora["r"], lora_alpha=lora["alpha"], lora_dropout=lora["dropout"],
                                             bias="none", target_modules=lora["target_modules"], task_type="CAUSAL_LM"))
    model.enable_input_require_grads()
    args = TrainingArguments(
        output_dir=str(ROOT / cfg["output_dir"]), per_device_train_batch_size=cfg["batch_size"],
        gradient_accumulation_steps=cfg["grad_accum"], num_train_epochs=cfg["epochs"], max_steps=max_steps,
        learning_rate=cfg["learning_rate"], warmup_steps=cfg["warmup_steps"], lr_scheduler_type="linear",
        weight_decay=cfg["weight_decay"], logging_steps=10, seed=cfg["seed"], report_to="none",
        save_strategy="no", gradient_checkpointing=torch.cuda.is_available(),
        gradient_checkpointing_kwargs={"use_reentrant": False}, use_cpu=not torch.cuda.is_available())
    Trainer(model=model, args=args, train_dataset=ds,
            data_collator=lambda b: collate(b, tok.pad_token_id)).train()
    model.save_pretrained(ROOT / cfg["output_dir"])
    return ROOT / cfg["output_dir"]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", default=str(ROOT / "configs/train.yaml"))
    p.add_argument("--max-steps", type=int, default=-1)
    p.add_argument("--limit", type=int)
    a = p.parse_args()
    cfg = yaml.safe_load(open(a.config, encoding="utf-8"))
    print("adapter saved to", train(cfg, a.max_steps, a.limit))


if __name__ == "__main__":
    main()
