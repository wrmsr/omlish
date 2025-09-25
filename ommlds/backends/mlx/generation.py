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
# https://github.com/ml-explore/mlx-lm/blob/ce2358d297af245b002e690623f00195b6507da0/mlx_lm/generate.py
import dataclasses as dc
import functools
import io
import sys
import typing as ta

import mlx.core as mx
import mlx_lm.models.cache
from mlx import nn

from omlish import check
from omlish import lang

from .caching import maybe_quantize_kv_cache
from .limits import wired_limit_context
from .tokenization import Tokenization


##


@lang.cached_function(lock=True)
def _generation_stream():
    return mx.new_stream(mx.default_device())


##


class LogitProcessor(ta.Protocol):
    def __call__(
            self,
            tokens: mx.array,
            logits: mx.array,
    ) -> mx.array:
        ...


@dc.dataclass(frozen=True, kw_only=True)
class PromptProgress:
    processed_tokens: int
    total_tokens: int


@dc.dataclass(frozen=True, kw_only=True)
class GenerationParams:
    # The maximum number of tokens. Use -1 for an infinite generator.
    max_tokens: int = 256

    # A sampler for sampling a token from a vector of log probabilities.
    sampler: ta.Callable[['mx.array'], 'mx.array'] | None = None

    # A list of functions that take tokens and logits and return the processed logits.
    logits_processors: ta.Sequence[LogitProcessor] | None = None

    # Step size for processing the prompt.
    prefill_step_size: int = 2048

    # A callback which takes the prompt tokens processed so far and the total number of prompt tokens.
    prompt_progress_callback: ta.Callable[[PromptProgress], None] | None = None

    #

    # A pre-computed prompt cache. Note, if provided, the cache will be updated in place.
    prompt_cache: ta.Any | None = None

    # Maximum size of the key-value cache. Old entries (except the first 4 tokens) will be overwritten.
    max_kv_size: int | None = None

    # Number of bits to use for KV cache quantization. None implies no cache quantization.
    kv_bits: int | None = None

    # Group size for KV cache quantization.
    kv_group_size: int = 64

    # Step to begin using a quantized KV cache. when kv_bits is non-None.
    quantized_kv_start: int = 0


#


class _GenerationStep(ta.NamedTuple):
    token: int
    logprobs: mx.array


def _generate_step(
        prompt: mx.array,
        model: nn.Module,
        params: GenerationParams = GenerationParams(),
) -> ta.Generator[_GenerationStep]:
    y = prompt
    tokens = None

    # Create the Kv cache for generation
    prompt_cache = params.prompt_cache
    if prompt_cache is None:
        prompt_cache = mlx_lm.models.cache.make_prompt_cache(
            model,
            max_kv_size=params.max_kv_size,
        )

    elif len(prompt_cache) != len(model.layers):
        raise ValueError('Wrong number of layers in the prompt cache.')

    quantize_cache_fn = functools.partial(
        maybe_quantize_kv_cache,
        quantized_kv_start=params.quantized_kv_start,
        kv_group_size=params.kv_group_size,
        kv_bits=params.kv_bits,
    )

    sampler = params.sampler
    if sampler is None:
        sampler = lambda x: mx.argmax(x, axis=-1)  # noqa

    def _step(y):
        with mx.stream(_generation_stream()):
            logits = model(y[None], cache=prompt_cache)
            logits = logits[:, -1, :]

            if (lps := params.logits_processors):
                nonlocal tokens
                tokens = mx.concat([tokens, y]) if tokens is not None else y

                for lp in lps:
                    logits = lp(tokens, logits)

            quantize_cache_fn(prompt_cache)

            logprobs = logits - mx.logsumexp(logits, keepdims=True)  # noqa
            y = sampler(logprobs)
            return y, logprobs.squeeze(0)

    with mx.stream(_generation_stream()):
        total_prompt_tokens = y.size
        prompt_processed_tokens = 0

        while y.size > params.prefill_step_size:
            model(y[:params.prefill_step_size][None], cache=prompt_cache)

            quantize_cache_fn(prompt_cache)

            mx.eval([c.state for c in prompt_cache])

            if (pcb := params.prompt_progress_callback) is not None:
                pcb(PromptProgress(
                    processed_tokens=prompt_processed_tokens,
                    total_tokens=total_prompt_tokens,
                ))

            prompt_processed_tokens += params.prefill_step_size

            y = y[params.prefill_step_size:]

            mx.clear_cache()

        y, logprobs = _step(y)

    mx.async_eval(y, logprobs)

    n = 0
    while True:
        if n != params.max_tokens:
            next_y, next_logprobs = _step(y)

            mx.async_eval(next_y, next_logprobs)

        if n == 0:
            mx.eval(y)

            if (pcb := params.prompt_progress_callback) is not None:
                pcb(PromptProgress(
                    processed_tokens=prompt_processed_tokens,
                    total_tokens=total_prompt_tokens,
                ))

        if n == params.max_tokens:
            break

        yield _GenerationStep(
            token=check.isinstance(y.item(), int),
            logprobs=logprobs,
        )

        if n % 256 == 0:
            mx.clear_cache()

        y, logprobs = next_y, next_logprobs  # noqa

        n += 1


##


@dc.dataclass(kw_only=True)
class GenerationOutput:
    # The next segment of decoded text. This can be an empty string.
    text: str

    # The next token.
    token: int

    # A vector of log probabilities.
    logprobs: mx.array

    # The number of tokens in the prompt.
    prompt_tokens: int

    # The number of generated tokens.
    generation_tokens: int

    # The reason the response is being sent.
    finish_reason: ta.Literal['stop', 'length'] | None = None


def stream_generate(
        model: nn.Module,
        tokenization: Tokenization,
        prompt: str | mx.array,
        params: GenerationParams = GenerationParams(),
) -> ta.Generator[GenerationOutput]:
    if not isinstance(prompt, mx.array):
        if isinstance(prompt, str):
            tokenizer = tokenization.tokenizer

            # Try to infer if special tokens are needed
            add_special_tokens = (
                tokenizer.bos_token is None or
                not prompt.startswith(tokenizer.bos_token)
            )

            prompt = tokenizer.encode(
                prompt,
                add_special_tokens=add_special_tokens,
            )

        prompt = mx.array(ta.cast(ta.Any, prompt))

    detokenizer = tokenization.detokenizer
    detokenizer.reset()

    token_generator = (
        (token, logprobs)
        for token, logprobs in _generate_step(
            prompt,
            model,
            params,
        )
    )

    with wired_limit_context(model, [_generation_stream()]):
        n = -1
        for n, (token, logprobs) in enumerate(token_generator):
            token = check.isinstance(token, int)
            if token in tokenization.eos_token_ids:
                break

            detokenizer.add_token(token)

            last_segment = detokenizer.last_segment()

            yield GenerationOutput(
                text=last_segment,
                token=token,
                logprobs=logprobs,
                prompt_tokens=prompt.size,
                generation_tokens=n + 1,
            )

    if n < 0:
        return

    detokenizer.finalize()

    last_segment = detokenizer.last_segment()

    yield GenerationOutput(
        text=last_segment,
        token=token,  # noqa
        logprobs=logprobs,  # noqa
        prompt_tokens=prompt.size,
        generation_tokens=n + 1,
        finish_reason='stop' if token in tokenization.eos_token_ids else 'length',
    )


##


def generate(
        model: nn.Module,
        tokenization: Tokenization,
        prompt: str | mx.array,
        params: GenerationParams = GenerationParams(),
        *,
        verbose: bool = False,
        verbose_out: ta.TextIO | None = None,
) -> str:
    vp: ta.Callable[..., None] | None = None
    if verbose:
        vp = functools.partial(print, file=verbose_out if verbose_out is not None else sys.stderr)
        vp('=' * 10)

    sb = io.StringIO()

    n = -1
    for n, gr in enumerate(stream_generate(  # noqa
        model,
        tokenization,
        prompt,
        params,
    )):
        if vp is not None:
            vp(gr.text, end='')

        sb.write(gr.text)

    if vp is not None:
        vp()
        vp('=' * 10)

        if n < 0:
            vp('No tokens generated.')
        else:
            vp(f'Prompt: {gr.prompt_tokens} tokens')  # noqa
            vp(f'Generation: {gr.generation_tokens} tokens')

        vp(f'Peak memory: {mx.get_peak_memory() / 1e9:.3f} GB')

    return sb.getvalue()
