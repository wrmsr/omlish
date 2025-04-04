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
import contextlib
import dataclasses as dc
import functools
import sys
import time
import typing as ta

from omlish import lang


if ta.TYPE_CHECKING:
    import mlx.core
    import mlx.nn
    import mlx.utils
    import mlx_lm.models.cache
    import mlx_lm.tokenizer_utils
    import mlx_lm.utils
    import transformers
else:
    mlx = lang.proxy_import('mlx', extras=[
        'core',
        'nn',
        'utils',
    ])
    mlx_lm = lang.proxy_import('mlx_lm', extras=[
        'models.cache',
        'tokenizer_utils',
        'utils',
    ])
    transformers = lang.proxy_import('transformers')


##


# A stream on the default device just for generation
@lang.cached_function
def generation_stream():
    return mlx.core.new_stream(mlx.core.default_device())


@contextlib.contextmanager
def wired_limit(model: 'mlx.nn.Module', streams: list['mlx.core.Stream'] | None = None):
    """
    A context manager to temporarily change the wired limit.

    Note, the wired limit should not be changed during an async eval.  If an async eval could be running pass in the
    streams to synchronize with prior to exiting the context manager.
    """

    model_bytes = mlx.utils.tree_reduce(
        lambda acc, x: acc + x.nbytes if isinstance(x, mlx.core.array) else acc, model, 0,
    )
    max_rec_size = mlx.core.metal.device_info()['max_recommended_working_set_size']
    if model_bytes > 0.9 * max_rec_size:
        model_mb = model_bytes // 2**20
        max_rec_mb = max_rec_size // 2**20
        print(
            f'[WARNING] Generating with a model that requires {model_mb} MB '
            f'which is close to the maximum recommended size of {max_rec_mb} '
            'MB. This can be slow. See the documentation for possible work-arounds: '
            'https://github.com/ml-explore/mlx-lm/tree/main#large-models',
        )
    old_limit = mlx.core.set_wired_limit(max_rec_size)
    try:
        yield None
    finally:
        if streams is not None:
            for s in streams:
                mlx.core.synchronize(s)
        else:
            mlx.core.synchronize()
        mlx.core.set_wired_limit(old_limit)


@dc.dataclass()
class GenerationResponse:
    """
    The output of :func:`stream_generate`.

    Args:
        text (str): The next segment of decoded text. This can be an empty string.
        token (int): The next token.
        from_draft (bool): Whether the token was generated by the draft model.
        logprobs (mx.array): A vector of log probabilities.
        prompt_tokens (int): The number of tokens in the prompt.
        prompt_tps (float): The prompt processing tokens-per-second.
        generation_tokens (int): The number of generated tokens.
        generation_tps (float): The tokens-per-second for generation.
        peak_memory (float): The peak memory used so far in GB.
        finish_reason (str): The reason the response is being sent: "length", "stop" or `None`
    """

    text: str
    token: int
    logprobs: 'mlx.core.array'
    from_draft: bool
    prompt_tokens: int
    prompt_tps: float
    generation_tokens: int
    generation_tps: float
    peak_memory: float
    finish_reason: str | None = None


def maybe_quantize_kv_cache(prompt_cache, quantized_kv_start, kv_group_size, kv_bits):
    if (
        kv_bits is not None
        and not isinstance(prompt_cache[0], mlx_lm.models.cache.QuantizedKVCache)
        and prompt_cache[0].offset > quantized_kv_start
    ):
        for i in range(len(prompt_cache)):
            if isinstance(prompt_cache[i], mlx_lm.models.cache.KVCache):
                prompt_cache[i] = prompt_cache[i].to_quantized(
                    group_size=kv_group_size, bits=kv_bits,
                )


def generate_step(
        prompt: 'mlx.core.array',
        model: 'mlx.nn.Module',
        *,
        max_tokens: int = 256,
        sampler: ta.Callable[['mlx.core.array'], 'mlx.core.array'] | None = None,
        logits_processors: list[ta.Callable[['mlx.core.array', 'mlx.core.array'], 'mlx.core.array']] | None = None,
        max_kv_size: int | None = None,
        prompt_cache: ta.Any | None = None,
        prefill_step_size: int = 2048,
        kv_bits: int | None = None,
        kv_group_size: int = 64,
        quantized_kv_start: int = 0,
        prompt_progress_callback: ta.Callable[[int, int], None] | None = None,
) -> ta.Generator[tuple['mlx.core.array', 'mlx.core.array'], None, None]:
    """
    A generator producing token ids based on the given prompt from the model.

    Args:
        prompt (mx.array): The input prompt.
        model (nn.Module): The model to use for generation.
        max_tokens (int): The maximum number of tokens. Use``-1`` for an infinite generator. Default: ``256``.
        sampler (Callable[[mx.array], mx.array], optional): A sampler for sampling a token from a vector of log
          probabilities. Default: ``None``.
        logits_processors (List[Callable[[mx.array, mx.array], mx.array]], optional): A list of functions that take
          tokens and logits and return the processed logits. Default: ``None``.
        max_kv_size (int, optional): Maximum size of the key-value cache. Old entries (except the first 4 tokens) will
          be overwritten.
        prompt_cache (List[Any], optional): A pre-computed prompt cache. Note, if provided, the cache will be updated in
          place.
        prefill_step_size (int): Step size for processing the prompt.
        kv_bits (int, optional): Number of bits to use for KV cache quantization. None implies no cache quantization.
          Default: ``None``.
        kv_group_size (int): Group size for KV cache quantization. Default: ``64``.
        quantized_kv_start (int): Step to begin using a quantized KV cache. when ``kv_bits`` is non-None. Default:
          ``0``.
        prompt_prorgress_callback (Callable[int, int]): A call-back which takes the prompt tokens processed so far and
          the total number of prompt tokens.

    Yields:
        Tuple[mx.array, mx.array]: One token and a vector of log probabilities.
    """

    y = prompt
    tokens = None

    # Create the KV cache for generation
    if prompt_cache is None:
        prompt_cache = mlx_lm.models.cache.make_prompt_cache(
            model,
            max_kv_size=max_kv_size,
        )
    elif len(prompt_cache) != len(model.layers):
        raise ValueError('Wrong number of layers in the prompt cache.')

    prompt_progress_callback = prompt_progress_callback or (lambda *_: None)

    quantize_cache_fn = functools.partial(
        maybe_quantize_kv_cache,
        quantized_kv_start=quantized_kv_start,
        kv_group_size=kv_group_size,
        kv_bits=kv_bits,
    )

    sampler = sampler or (lambda x: mlx.core.argmax(x, axis=-1))

    def _step(y):
        with mlx.core.stream(generation_stream()):
            logits = model(y[None], cache=prompt_cache)
            logits = logits[:, -1, :]

            if logits_processors:
                nonlocal tokens
                tokens = mlx.core.concat([tokens, y]) if tokens is not None else y

                for processor in logits_processors:
                    logits = processor(tokens, logits)

            quantize_cache_fn(prompt_cache)

            logprobs = logits - mlx.core.logsumexp(logits, keepdims=True)
            y = sampler(logprobs)
            return y, logprobs.squeeze(0)

    with mlx.core.stream(generation_stream()):
        total_prompt_tokens = y.size
        prompt_processed_tokens = 0
        while y.size > prefill_step_size:
            model(y[:prefill_step_size][None], cache=prompt_cache)
            quantize_cache_fn(prompt_cache)
            mlx.core.eval([c.state for c in prompt_cache])
            prompt_progress_callback(prompt_processed_tokens, total_prompt_tokens)
            prompt_processed_tokens += prefill_step_size
            y = y[prefill_step_size:]
            mlx.core.clear_cache()

        y, logprobs = _step(y)

    mlx.core.async_eval(y, logprobs)
    n = 0
    while True:
        if n != max_tokens:
            next_y, next_logprobs = _step(y)
            mlx.core.async_eval(next_y, next_logprobs)
        if n == 0:
            mlx.core.eval(y)
            prompt_progress_callback(total_prompt_tokens, total_prompt_tokens)
        if n == max_tokens:
            break
        yield y.item(), logprobs
        if n % 256 == 0:
            mlx.core.clear_cache()
        y, logprobs = next_y, next_logprobs
        n += 1


def speculative_generate_step(
        prompt: 'mlx.core.array',
        model: 'mlx.nn.Module',
        draft_model: 'mlx.nn.Module',
        *,
        num_draft_tokens=2,
        max_tokens: int = 256,
        sampler: ta.Callable[['mlx.core.array'], 'mlx.core.array'] | None = None,
        logits_processors: list[ta.Callable[['mlx.core.array', 'mlx.core.array'], 'mlx.core.array']] | None = None,
        prompt_cache: ta.Any | None = None,
        prefill_step_size: int = 512,
        kv_bits: int | None = None,
        kv_group_size: int = 64,
        quantized_kv_start: int = 0,
) -> ta.Generator[tuple['mlx.core.array', 'mlx.core.array', bool], None, None]:
    """
    A generator producing token ids based on the given prompt from the model.

    Args:
        prompt (mx.array): The input prompt.
        model (nn.Module): The model to use for generation.
        draft_model (nn.Module): The draft model for speculative decoding.
        num_draft_tokens (int, optional): The number of draft tokens for speculative decoding. Default: ``2``.
        max_tokens (int): The maximum number of tokens. Use``-1`` for an infinite generator. Default: ``256``.
        sampler (Callable[mx.array, mx.array], optional): A sampler for sampling a token from a vector of log
          probabilities. Default: ``None``.
        logits_processors (List[Callable[[mx.array, mx.array], mx.array]], optional): A list of functions that take
          tokens and logits and return the processed logits. Default: ``None``.
        prompt_cache (List[Any], optional): A pre-computed prompt cache. Note, if provided, the cache will be updated in
          place. The cache must be trimmable.
        prefill_step_size (int): Step size for processing the prompt.
        kv_bits (int, optional): Number of bits to use for KV cache quantization. None implies no cache quantization.
          Default: ``None``.
        kv_group_size (int): Group size for KV cache quantization. Default: ``64``.
        quantized_kv_start (int): Step to begin using a quantized KV cache. when ``kv_bits`` is non-None. Default:
          ``0``.

    Yields:
        Tuple[mx.array, mx.array, bool]: One token, a vector of log probabilities, and a bool indicating if the token
          was generated by the draft model
    """

    y = prompt.astype(mlx.core.uint32)
    prev_tokens = None

    # Create the KV cache for generation
    if prompt_cache is None:
        model_cache = mlx_lm.models.cache.make_prompt_cache(model)
        draft_cache = mlx_lm.models.cache.make_prompt_cache(draft_model)
    elif len(prompt_cache) != (len(model.layers) + len(draft_model.layers)):
        raise ValueError('Wrong number of layers in the prompt cache.')
    else:
        model_cache = prompt_cache[: len(model.layers)]
        draft_cache = prompt_cache[len(model.layers):]

    sampler = sampler or (lambda x: mlx.core.argmax(x, axis=-1))

    quantize_cache_fn = functools.partial(
        maybe_quantize_kv_cache,
        quantized_kv_start=quantized_kv_start,
        kv_group_size=kv_group_size,
        kv_bits=kv_bits,
    )

    def _process_and_sample(tokens, logits):
        if logits_processors:
            for processor in logits_processors:
                logits = processor(tokens, logits)

        logprobs = logits - mlx.core.logsumexp(logits, axis=-1, keepdims=True)
        y = sampler(logprobs)
        return y, logprobs

    def _step(model, cache, y, n_predict=1):
        with mlx.core.stream(generation_stream()):
            logits = model(y[None], cache=cache)
            logits = logits[:, -n_predict:, :]

            quantize_cache_fn(cache)
            if logits_processors:
                nonlocal prev_tokens
                out_y, out_logprobs = [], []
                if n_predict > 1:
                    y = y[: -(n_predict - 1)]
                for i in range(n_predict):
                    prev_tokens = (
                        mlx.core.concat([prev_tokens, y]) if prev_tokens is not None else y
                    )
                    y, logprobs = _process_and_sample(prev_tokens, logits[:, i, :])
                    out_y.append(y)
                    out_logprobs.append(logprobs)
                return mlx.core.concatenate(out_y, axis=0), mlx.core.concatenate(
                    out_logprobs, axis=0,
                )
            else:
                return _process_and_sample(None, logits.squeeze(0))

    def _prefill(model, cache, y):
        while y.size > prefill_step_size:
            model(y[:prefill_step_size][None], cache=cache)
            quantize_cache_fn(cache)
            mlx.core.eval([c.state for c in cache])
            y = y[prefill_step_size:]
            mlx.core.clear_cache()
        return y

    def _rewind_cache(num_draft, num_accept):
        mlx_lm.models.cache.trim_prompt_cache(model_cache, num_draft - num_accept)
        mlx_lm.models.cache.trim_prompt_cache(draft_cache, max(num_draft - num_accept - 1, 0))

    def _draft_generate(y, num_draft):
        if num_draft == 0:
            return mlx.core.array([], mlx.core.uint32)
        ys = []
        for _ in range(num_draft):
            y, _ = _step(draft_model, draft_cache, y)
            mlx.core.async_eval(y)
            ys.append(y)
        return mlx.core.concatenate(ys)

    with mlx.core.stream(generation_stream()):
        draft_y = _prefill(draft_model, draft_cache, y)
        y = _prefill(model, model_cache, y)

    ntoks = 0
    # Set these so the finally block doesn't raise
    num_draft = 0
    n = 0
    try:
        while True:
            num_draft = min(max_tokens - ntoks, num_draft_tokens)
            draft_tokens = _draft_generate(draft_y, num_draft)
            if prev_tokens is not None:
                prev_tokens = prev_tokens[: prev_tokens.size - y.size - num_draft + 1]
            y = mlx.core.concatenate([y, draft_tokens])
            tokens, logprobs = _step(model, model_cache, y, num_draft + 1)
            mlx.core.eval(tokens, draft_tokens)
            draft_tokens = draft_tokens.tolist()
            tokens = tokens.tolist()
            n = 0
            while n < num_draft:
                tn, dtn, lpn = tokens[n], draft_tokens[n], logprobs[n]
                if tn != dtn:
                    break
                n += 1
                ntoks += 1
                yield tn, lpn, True
                if ntoks == max_tokens:
                    break
            if ntoks < max_tokens:
                ntoks += 1
                yield tokens[n], logprobs[n], False

            if ntoks == max_tokens:
                break

            y = mlx.core.array([tokens[n]], mlx.core.uint32)
            draft_y = y

            # If we accepted all the draft tokens, include the last
            # draft token in the next draft step since it hasn't been
            # processed yet by the draft model
            if n == num_draft:
                draft_y = mlx.core.concatenate(
                    [mlx.core.array(draft_tokens[-1:], mlx.core.uint32), draft_y],
                )

            if prev_tokens is not None:
                prev_tokens = prev_tokens[: -max(num_draft - n, 1)]
            _rewind_cache(num_draft, n)
    finally:
        _rewind_cache(num_draft, n)


def stream_generate(
        model: 'mlx.nn.Module',
        tokenizer: ta.Union['transformers.PreTrainedTokenizer', 'mlx_lm.tokenizer_utils.TokenizerWrapper'],
        prompt: ta.Union[str, 'mlx.core.array', list[int]],
        *,
        draft_model: ta.Optional['mlx.nn.Module'] = None,
        **kwargs: ta.Any,
) -> ta.Generator[GenerationResponse, None, None]:
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

    if not isinstance(tokenizer, mlx_lm.tokenizer_utils.TokenizerWrapper):
        tokenizer = mlx_lm.tokenizer_utils.TokenizerWrapper(tokenizer)

    if not isinstance(prompt, mlx.core.array):
        if isinstance(prompt, str):
            # Try to infer if special tokens are needed
            add_special_tokens = tokenizer.bos_token is None or not prompt.startswith(
                tokenizer.bos_token,
            )
            prompt = tokenizer.encode(prompt, add_special_tokens=add_special_tokens)
        prompt = mlx.core.array(prompt)

    detokenizer = tokenizer.detokenizer

    if draft_model is None:
        kwargs.pop('num_draft_tokens', None)
        # from_draft always false for non-speculative generation
        token_generator = (
            (token, logprobs, False) for token, logprobs
            in generate_step(
                prompt,
                model,
                **kwargs,
            )
        )
    else:
        kwargs.pop('max_kv_size', None)
        token_generator = speculative_generate_step(
            prompt,
            model,
            draft_model,
            **kwargs,
        )

    with wired_limit(model, [generation_stream()]):
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

            yield GenerationResponse(
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

        # NOTE: Destructive property access
        last_segment = detokenizer.last_segment

        yield GenerationResponse(
            text=last_segment,
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
        tokenizer: ta.Union['transformers.PreTrainedTokenizer', 'mlx_lm.tokenizer_utils.TokenizerWrapper'],
        prompt: str | list[int],
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
       verbose (bool): If ``True``, print tokens and timing information. Default: ``False``.
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
