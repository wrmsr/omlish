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
import contextlib
import sys
import typing as ta

import mlx.core as mx
import mlx.utils
from mlx import nn


##


@contextlib.contextmanager
def wired_limit_context(
        model: nn.Module,
        streams: ta.Iterable[mx.Stream] | None = None,
) -> ta.Generator[None]:
    """
    A context manager to temporarily change the wired limit.

    Note, the wired limit should not be changed during an async eval. If an async eval could be running pass in the
    streams to synchronize with prior to exiting the context manager.
    """

    if not mx.metal.is_available():
        yield
        return

    model_bytes = mlx.utils.tree_reduce(
        lambda acc, x: acc + x.nbytes if isinstance(x, mx.array) else acc,
        model,
        0,
    )

    max_rec_size = int(mx.metal.device_info()['max_recommended_working_set_size'])
    if model_bytes > 0.9 * max_rec_size:
        model_mb = model_bytes // 2**20
        max_rec_mb = max_rec_size // 2**20
        print(
            f'[WARNING] Generating with a model that requires {model_mb} MB which is close to the maximum recommended '
            f'size of {max_rec_mb} MB. This can be slow. See the documentation for possible workarounds: '
            f'https://github.com/ml-explore/mlx-lm/tree/main#large-models',
            file=sys.stderr,
        )

    old_limit = mx.set_wired_limit(max_rec_size)
    try:
        yield

    finally:
        if streams is not None:
            for s in streams:
                mx.synchronize(s)
        else:
            mx.synchronize()

        mx.set_wired_limit(old_limit)
