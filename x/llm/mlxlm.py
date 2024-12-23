import mlx_lm


def _main() -> None:
    model, tokenizer = mlx_lm.load(
        # 'mlx-community/DeepSeek-Coder-V2-Lite-Instruct-8bit'
        'mlx-community/Llama-3.3-70B-Instruct-4bit',
        # 'mlx-community/Llama-3.3-70B-Instruct-6bit'
        # 'mlx-community/Llama-3.3-70B-Instruct-8bit'
        # 'mlx-community/Mixtral-8x7B-Instruct-v0.1'
        # 'mlx-community/QwQ-32B-Preview-8bit'
        # 'mlx-community/QwQ-32B-Preview-bf16'
        # 'mlx-community/Qwen2.5-32B-Instruct-8bit'
        # 'mlx-community/Qwen2.5-Coder-32B-Instruct-8bit'
        # 'mlx-community/mamba-2.8b-hf-f16'
    )

    prompt = 'hello'

    if (
            hasattr(tokenizer, 'apply_chat_template') and
            tokenizer.chat_template is not None
    ):
        messages = [{'role': 'user', 'content': prompt}]

        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

    response = mlx_lm.generate(
        model,
        tokenizer,
        prompt=prompt,
        verbose=True,
    )

    print(response)


if __name__ == '__main__':
    _main()
