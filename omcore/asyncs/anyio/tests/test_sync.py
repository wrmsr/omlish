import functools

import anyio.to_thread
import pytest

from .... import lang
from ..sync import LazyFn


@pytest.mark.asyncs('asyncio')
async def test_lazy_fn():
    c = 0

    async def fn():
        nonlocal c
        c += 1
        return 420

    lfn = LazyFn(fn)

    assert c == 0
    assert await lfn.get() == 420
    assert c == 1
    assert await lfn.get() == 420
    assert c == 1


@pytest.mark.asyncs('asyncio')
async def test_lazy_fn2():
    c = 0

    def fn():
        nonlocal c
        c += 1
        return 420

    lfn = LazyFn(lang.as_async(fn))

    assert c == 0
    assert await lfn.get() == 420
    assert c == 1
    assert await lfn.get() == 420
    assert c == 1


@pytest.mark.asyncs('asyncio')
async def test_lazy_fn3():
    c = 0

    def fn():
        nonlocal c
        c += 1
        return 420

    lfn = LazyFn(functools.partial(anyio.to_thread.run_sync, fn))

    assert c == 0
    assert await lfn.get() == 420
    assert c == 1
    assert await lfn.get() == 420
    assert c == 1
