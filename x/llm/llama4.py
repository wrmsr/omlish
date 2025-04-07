from transformers import AutoProcessor, Llama4ForConditionalGeneration
import torch


def _main() -> None:
    model_id = (
        # "meta-llama/Llama-4-Maverick-17B-128E-Instruct"
        'unsloth/Llama-4-Scout-17B-16E-Instruct-unsloth-bnb-4bit'
    )

    processor = AutoProcessor.from_pretrained(model_id)
    model = Llama4ForConditionalGeneration.from_pretrained(
        model_id,
        attn_implementation="flex_attention",
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )

    url1 = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/0052a70beed5bf71b92610a43a52df6d286cd5f3/diffusers/rabbit.jpg"
    url2 = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/datasets/cat_style_layout.png"
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "url": url1},
                {"type": "image", "url": url2},
                {"type": "text", "text": "Can you describe how these two images are similar, and how they differ?"},
            ]
        },
    ]

    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
    )

    response = processor.batch_decode(outputs[:, inputs["input_ids"].shape[-1]:])[0]
    print(response)
    print(outputs[0])


if __name__ == '__main__':
    _main()
