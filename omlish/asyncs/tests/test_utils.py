import contextlib

import pytest

from ... import lang
from ..utils import call_with_async_exit_stack


@pytest.mark.asyncs
async def test_call_with_async_exit_stack():
    c = 0

    async def foo(aes: contextlib.AsyncExitStack, i: int) -> int:
        async def bar():
            nonlocal c
            c += 1

        await aes.enter_async_context(lang.adefer(bar()))  # noqa
        return i + 1

    assert (await call_with_async_exit_stack(foo, 5)) == 6
    assert c == 1
