"""
https://simonwillison.net/2024/Nov/12/qwen25-coder/

--

uv run --with mlx-lm \
  mlx_lm.generate \
  --model mlx-community/Qwen2.5-Coder-32B-Instruct-8bit \
  --max-tokens 4000 \
  --prompt 'write me a python function that renders a mandelbrot fractal as wide as the current terminal'
"""
import mlx_lm.utils


def _main():
    prompt = 'write me a python function that renders a mandelbrot fractal as wide as the current terminal'
    model_path = 'mlx-community/Qwen2.5-Coder-32B-Instruct-8bit'
    max_tokens = 4000

    model, tokenizer = mlx_lm.utils.load(
        model_path,
        adapter_path=None,
        tokenizer_config={},
    )

    mlx_lm.utils.generate(
        model,
        tokenizer,
        prompt,
        max_tokens,
        formatter=None,
        kv_bits=None,
        kv_group_size=64,
        max_kv_size=None,
        prompt_cache=None,
        quantized_kv_start=5000,
        temp=0.0,
        top_p=1.0,
        verbose=True,
    )


if __name__ == '__main__':
    _main()
