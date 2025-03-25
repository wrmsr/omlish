# MIT License
#
# Copyright © 2023 Apple Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# https://github.com/ml-explore/mlx-lm/blob/455cdac5dfd7cdd5f6318885647a86bcdbe79000/mlx_lm/generate.py
import sys
import time
import typing as ta

from omlish import lang


if ta.TYPE_CHECKING:
    import mlx.core
    import mlx.nn
    import mlx_lm.utils
    import transformers
else:
    mlx = lang.proxy_import('mlx', extras=['core', 'nn'])
    mlx_lm = lang.proxy_import('mlx_lm', extras=['utils'])
    transformers = lang.proxy_import('transformers')


##


def stream_generate(
        model: 'mlx.nn.Module',
        tokenizer: ta.Union['transformers.PreTrainedTokenizer', 'mlx_lm.utils.TokenizerWrapper'],
        prompt: ta.Union[str, 'mlx.core.array', list[int]],
        *,
        draft_model: ta.Optional['mlx.nn.Module'] = None,
        **kwargs: ta.Any,
) -> ta.Generator['mlx_lm.utils.GenerationResponse', None, None]:
    """
    A generator producing text based on the given prompt from the model.

    Args:
        model (nn.Module): The model to use for generation.
        tokenizer (PreTrainedTokenizer): The tokenizer.
        prompt (Union[str, mx.array, List[int]]): The input prompt string or integer tokens.
        draft_model (Optional[nn.Module]): An optional draft model. If provided then speculative decoding is used. The
          draft model must use the same tokenizer as the main model. Default: ``None``.
        kwargs: The remaining options get passed to :func:`generate_step`. See :func:`generate_step` for more details.

    Yields:
        GenerationResponse: An instance containing the generated text segment and associated metadata. See
          :class:`GenerationResponse` for details.
    """

    if not isinstance(tokenizer, mlx_lm.utils.TokenizerWrapper):
        tokenizer = mlx_lm.utils.TokenizerWrapper(tokenizer)

    if not isinstance(prompt, mlx.core.array):
        if isinstance(prompt, str):
            # Try to infer if special tokens are needed
            add_special_tokens = tokenizer.bos_token is None or not prompt.startswith(tokenizer.bos_token)
            prompt = tokenizer.encode(prompt, add_special_tokens=add_special_tokens)

        prompt = mlx.core.array(prompt)

    detokenizer = tokenizer.detokenizer

    token_generator: ta.Any
    if draft_model is None:
        kwargs.pop('num_draft_tokens', None)
        token_generator = mlx_lm.utils.generate_step(prompt, model, **kwargs)
        # from_draft always false for non-speculative generation
        token_generator = (
            (token, logprobs, False)
            for token, logprobs in token_generator
        )

    else:
        kwargs.pop('max_kv_size', None)
        token_generator = mlx_lm.utils.speculative_generate_step(
            prompt,
            model,
            draft_model,
            **kwargs,
        )

    with mlx_lm.utils.wired_limit(model, [mlx_lm.utils.generation_stream]):
        detokenizer.reset()
        tic = time.perf_counter()
        for n, (token, logprobs, from_draft) in enumerate(token_generator):
            if n == 0:
                prompt_time = time.perf_counter() - tic
                prompt_tps = prompt.size / prompt_time
                tic = time.perf_counter()
            if token in tokenizer.eos_token_ids:
                break

            detokenizer.add_token(token)

            # NOTE: Destructive property access
            last_segment = detokenizer.last_segment

            yield mlx_lm.utils.GenerationResponse(
                text=last_segment,
                token=token,
                logprobs=logprobs,
                from_draft=from_draft,
                prompt_tokens=prompt.size,
                prompt_tps=prompt_tps,
                generation_tokens=n + 1,
                generation_tps=(n + 1) / (time.perf_counter() - tic),
                peak_memory=mlx.core.get_peak_memory() / 1e9,
                finish_reason=None,
            )

        detokenizer.finalize()
        yield mlx_lm.utils.GenerationResponse(
            text=detokenizer.last_segment,
            token=token,
            logprobs=logprobs,
            from_draft=from_draft,
            prompt_tokens=prompt.size,
            prompt_tps=prompt_tps,
            generation_tokens=n + 1,
            generation_tps=(n + 1) / (time.perf_counter() - tic),
            peak_memory=mlx.core.get_peak_memory() / 1e9,
            finish_reason='stop' if token in tokenizer.eos_token_ids else 'length',
        )


def generate(
        model: 'mlx.nn.Module',
        tokenizer: ta.Union['transformers.PreTrainedTokenizer', 'mlx_lm.utils.TokenizerWrapper'],
        prompt: str | list[int],
        *,
        verbose: bool = False,
        formatter: ta.Callable | None = None,
        **kwargs: ta.Any,
) -> str:
    """
    Generate a complete response from the model.

    Args:
       model (nn.Module): The language model.
       tokenizer (PreTrainedTokenizer): The tokenizer.
       prompt (Union[str, List[int]]): The input prompt string or integer tokens.
       verbose (bool): If ``True``, print tokens and timing information.
           Default: ``False``.
       kwargs: The remaining options get passed to :func:`stream_generate`. See :func:`stream_generate` for more
         details.
    """

    if formatter is not None:
        print(
            '[Warning] Text formatting is deprecated and no longer used. '
            'The argument will be removed in a future version.',
            file=sys.stderr,
        )

    if verbose:
        print('=' * 10, file=sys.stderr)

    text = ''
    for response in stream_generate(model, tokenizer, prompt, **kwargs):
        if verbose:
            print(response.text, end='', flush=True, file=sys.stderr)

        text += response.text

    if verbose:
        print(file=sys.stderr)
        print('=' * 10, file=sys.stderr)

        if len(text) == 0:
            print('No text generated for this prompt', file=sys.stderr)
            return text

        print(
            f"Prompt: {response.prompt_tokens} tokens, "  # noqa
            f'{response.prompt_tps:.3f} tokens-per-sec',
            file=sys.stderr,
        )

        print(
            f'Generation: {response.generation_tokens} tokens, '
            f'{response.generation_tps:.3f} tokens-per-sec',
            file=sys.stderr,
        )

        print(f'Peak memory: {response.peak_memory:.3f} GB', file=sys.stderr)

    return text
