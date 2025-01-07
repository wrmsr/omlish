# Based on pytest-trio, licensed under the MIT license, duplicated below.
#
#  https://github.com/python-trio/pytest-trio/tree/cd6cc14b061d34f35980e38c44052108ed5402d1
#
# The MIT License (MIT)
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
import functools
import sys
import typing as ta

import pytest
from _pytest.outcomes import Skipped  # noqa
from _pytest.outcomes import XFailed  # noqa

from ...... import lang
from .base import AsyncsBackend


if ta.TYPE_CHECKING:
    import trio
else:
    trio = lang.proxy_import('trio', extras=['abc'])


class TrioAsyncsBackend(AsyncsBackend):
    name = 'trio'

    def is_available(self) -> bool:
        return lang.can_import('trio')

    def is_imported(self) -> bool:
        return 'trio' in sys.modules

    #

    def wrap_runner(self, fn):
        @functools.wraps(fn)
        def wrapper(**kwargs):
            __tracebackhide__ = True

            clocks = {k: c for k, c in kwargs.items() if isinstance(c, trio.abc.Clock)}
            if not clocks:
                clock = None
            elif len(clocks) == 1:
                clock = list(clocks.values())[0]  # noqa
            else:
                raise ValueError(f'Expected at most one Clock in kwargs, got {clocks!r}')

            instruments = [i for i in kwargs.values() if isinstance(i, trio.abc.Instrument)]

            try:
                return trio.run(
                    functools.partial(fn, **kwargs),
                    clock=clock,
                    instruments=instruments,
                )

            except BaseExceptionGroup as eg:
                queue: list[BaseException] = [eg]
                leaves = []

                while queue:
                    ex = queue.pop()
                    if isinstance(ex, BaseExceptionGroup):
                        queue.extend(ex.exceptions)
                    else:
                        leaves.append(ex)

                if len(leaves) == 1:
                    if isinstance(leaves[0], XFailed):
                        pytest.xfail()
                    if isinstance(leaves[0], Skipped):
                        pytest.skip()

                # Since our leaf exceptions don't consist of exactly one 'magic' skipped or xfailed exception, re-raise
                # the whole group.
                raise

        return wrapper
