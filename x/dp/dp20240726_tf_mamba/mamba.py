"""
https://huggingface.co/docs/transformers/en/model_doc/mamba
"""
from datasets import load_dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM
from transformers import AutoTokenizer
from transformers import TrainingArguments
from trl import SFTTrainer


if __name__ == '__main__':
    model_id = "state-spaces/mamba-130m-hf"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id)

    input_ids = tokenizer("Hey how are you doing?", return_tensors="pt")["input_ids"]
    out = model.generate(input_ids, max_new_tokens=10)
    print(tokenizer.batch_decode(out))

    dataset = load_dataset("Abirate/english_quotes", split="train")
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        logging_dir='./logs',
        logging_steps=10,
        learning_rate=2e-3
    )
    lora_config = LoraConfig(
        r=8,
        target_modules=["x_proj", "embeddings", "in_proj", "out_proj"],
        task_type="CAUSAL_LM",
        bias="none"
    )
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        args=training_args,
        peft_config=lora_config,
        train_dataset=dataset,
        dataset_text_field="quote",
    )
    trainer.train()
