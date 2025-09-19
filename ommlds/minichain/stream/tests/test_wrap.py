import typing as ta

import pytest

from omlish import lang

from ...services import Request
from ..wrap import WrappedStreamService
from .test_services import FooStreamService


class WrappedFooStreamService(WrappedStreamService):
    @ta.override
    async def _process_value(self, v: str) -> ta.Iterable[str]:
        return [v + '?']


@pytest.mark.asyncs('asyncio')
async def test_wrap_async():
    foo_svc = FooStreamService(do_sleep=True)
    lst: list = []
    async with (await WrappedFooStreamService(foo_svc).invoke(Request('hi there!'))).v as it:  # noqa
        async for e in it:
            lst.append(e)
    assert foo_svc.num_sleeps == 10
    assert foo_svc.ran_finally
    assert lst == [c + '!?' for c in 'hi there!']


def test_wrap_sync():
    async def inner():
        foo_svc = FooStreamService(do_sleep=False)
        lst: list = []
        async with (await WrappedFooStreamService(foo_svc).invoke(Request('hi there!'))).v as it:  # noqa
            async for e in it:
                lst.append(e)
        assert foo_svc.num_sleeps == 0
        assert foo_svc.ran_finally
        return lst

    lst = lang.sync_await(inner())
    assert lst == [c + '!?' for c in 'hi there!']


@pytest.mark.asyncs('asyncio')
async def test_wrap_async_break_early():
    foo_svc = FooStreamService(do_sleep=True)
    lst: list = []
    async with (await WrappedFooStreamService(foo_svc).invoke(Request('hi there!'))).v as it:  # noqa
        for _ in range(4):
            lst.append(await it.__anext__())
    assert foo_svc.num_sleeps == 4
    assert foo_svc.ran_finally
    assert lst == [c + '!?' for c in 'hi there!'[:4]]


def test_wrap_sync_break_early():
    async def inner():
        foo_svc = FooStreamService(do_sleep=False)
        lst: list = []
        async with (await WrappedFooStreamService(foo_svc).invoke(Request('hi there!'))).v as it:  # noqa
            for _ in range(4):
                lst.append(await it.__anext__())
        assert foo_svc.num_sleeps == 0
        assert foo_svc.ran_finally
        return lst

    lst = lang.sync_await(inner())
    assert lst == [c + '!?' for c in 'hi there!'[:4]]
