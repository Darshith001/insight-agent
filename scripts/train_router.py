"""Fine-tune DistilBERT with LoRA to classify questions as fast/smart.

Run:
    python scripts/train_router.py --data data/router.jsonl --out out/router

Data format (jsonl): {"question": "...", "label": 0 or 1}  (0=fast, 1=smart)
"""
from __future__ import annotations
import argparse, json, os
from datasets import Dataset
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, DataCollatorWithPadding,
)
from peft import LoraConfig, get_peft_model, TaskType

BASE = "distilbert-base-uncased"


def load(path: str) -> Dataset:
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    return Dataset.from_list(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default="out/router")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--bs", type=int, default=32)
    ap.add_argument("--lr", type=float, default=2e-4)
    args = ap.parse_args()

    tok = AutoTokenizer.from_pretrained(BASE)
    ds = load(args.data).train_test_split(test_size=0.1, seed=42)

    def tokenize(b):
        return tok(b["question"], truncation=True, max_length=128)

    ds = ds.map(tokenize, batched=True)

    base = AutoModelForSequenceClassification.from_pretrained(BASE, num_labels=2)
    model = get_peft_model(base, LoraConfig(
        task_type=TaskType.SEQ_CLS, r=16, lora_alpha=32,
        lora_dropout=0.05, target_modules=["q_lin", "v_lin"],
    ))
    model.print_trainable_parameters()

    args_tr = TrainingArguments(
        output_dir=args.out,
        per_device_train_batch_size=args.bs,
        per_device_eval_batch_size=args.bs,
        num_train_epochs=args.epochs,
        learning_rate=args.lr,
        eval_strategy="epoch",
        save_strategy="epoch",
        fp16=True,
        logging_steps=20,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
    )

    trainer = Trainer(
        model=model, args=args_tr,
        train_dataset=ds["train"], eval_dataset=ds["test"],
        data_collator=DataCollatorWithPadding(tok),
        tokenizer=tok,
    )
    trainer.train()
    model.merge_and_unload().save_pretrained(args.out)
    tok.save_pretrained(args.out)
    print(f"Saved router to {args.out}")


if __name__ == "__main__":
    main()
