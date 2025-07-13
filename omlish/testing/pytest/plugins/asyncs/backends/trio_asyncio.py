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

from _pytest.outcomes import Skipped  # noqa
from _pytest.outcomes import XFailed  # noqa

from ...... import cached
from ...... import lang
from ......diag import pydevd as pdu
from .base import AsyncsBackend


if ta.TYPE_CHECKING:
    import trio_asyncio
else:
    trio = lang.proxy_import('trio', extras=['abc'])
    trio_asyncio = lang.proxy_import('trio_asyncio')


##


class TrioAsyncioAsyncsBackend(AsyncsBackend):
    name = 'trio_asyncio'

    def is_available(self) -> bool:
        return lang.can_import('trio_asyncio')

    def is_imported(self) -> bool:
        return 'trio_asyncio' in sys.modules

    #

    @cached.function
    def _prepare(self) -> None:
        # NOTE: Importing it here is apparently necessary to get its patching working - otherwise fails later with
        # `no running event loop` in anyio._backends._asyncio and such.
        import trio_asyncio  # noqa

        if pdu.is_present():
            pdu.patch_for_trio_asyncio()

    def prepare_for_metafunc(self, metafunc) -> None:
        self._prepare()

    #

    def wrap_runner(self, fn):
        @functools.wraps(fn)
        def wrapper(**kwargs):
            return trio_asyncio.run(
                trio_asyncio.aio_as_trio(
                    functools.partial(fn, **kwargs),
                ),
            )

        return wrapper

    async def install_context(self, contextvars_ctx):
        # Seemingly no longer necessary?
        # https://github.com/python-trio/pytest-trio/commit/ef0cd267ea62188a8e475c66cb584e7a2addc02a

        # # This is a gross hack. I guess Trio should provide a context= argument to start_soon/start?
        # task = trio.lowlevel.current_task()
        # if CANARY in task.context:
        #     return

        # task.context = contextvars_ctx

        # # Force a yield so we pick up the new context
        # await trio.sleep(0)

        pass
