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
import typing as ta

import mlx_lm.models.cache


##


def maybe_quantize_kv_cache(
        prompt_cache: ta.MutableSequence[ta.Any],
        *,
        kv_bits: int | None,
        kv_group_size: int,
        quantized_kv_start: int,
) -> None:
    if not (
            kv_bits is not None and
            not isinstance(prompt_cache[0], mlx_lm.models.cache.QuantizedKVCache) and
            prompt_cache[0].offset > quantized_kv_start
    ):
        return

    for i in range(len(prompt_cache)):
        if isinstance(prompt_cache[i], mlx_lm.models.cache.KVCache):
            prompt_cache[i] = prompt_cache[i].to_quantized(
                bits=kv_bits,
                group_size=kv_group_size,
            )
