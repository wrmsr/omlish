import asyncio

import pytest

from omcore import lang

from ..streams import Stream
from ..streams import StreamSink
from ..streams import new_stream


class FooStreamService:
    def __init__(self, *, do_sleep: bool = False) -> None:
        super().__init__()

        self.do_sleep = do_sleep
        self.num_sleeps = 0
        self.ran_finally = False

    async def invoke(self, v: str) -> Stream[str, int]:
        async def inner(sink: StreamSink[str]) -> int:
            try:
                i = 0
                for c in v:
                    i += 1
                    await sink.emit(c + '!')
                    if self.do_sleep:
                        await asyncio.sleep(.1)
                        self.num_sleeps += 1
                return i
            finally:
                if self.do_sleep:
                    await asyncio.sleep(.1)
                    self.num_sleeps += 1
                self.ran_finally = True
        return await new_stream(inner)


@pytest.mark.asyncs('asyncio')
async def test_foo_stream_service():
    lst: list = []
    async with (await (svc := FooStreamService(do_sleep=True)).invoke('hi there!')) as it:
        async for e in it:
            lst.append(e)
    assert svc.num_sleeps == 10
    assert svc.ran_finally
    assert lst == [c + '!' for c in 'hi there!']
    assert it.result.must() == 9


@pytest.mark.asyncs('asyncio')
async def test_foo_stream_service_break_early():
    lst: list = []
    async with (await (svc := FooStreamService(do_sleep=True)).invoke('hi there!')) as it:
        for _ in range(4):
            lst.append(await it.__anext__())
    assert svc.num_sleeps == 4
    assert svc.ran_finally
    assert lst == [c + '!' for c in 'hi there!'[:4]]


def test_foo_stream_service_sync():
    svc = FooStreamService()
    with lang.sync_async_with(lang.sync_await(svc.invoke('hi there!'))) as it:
        lst = lang.sync_async_list(it)
    assert svc.num_sleeps == 0
    assert svc.ran_finally
    assert lst == [c + '!' for c in 'hi there!']


def test_foo_stream_service_sync_break_early():
    svc = FooStreamService()
    lst: list = []
    with lang.sync_async_with(lang.sync_await(svc.invoke('hi there!'))) as it:
        for _ in range(4):
            lst.append(lang.sync_await(it.__anext__()))
    assert svc.num_sleeps == 0
    assert svc.ran_finally
    assert lst == [c + '!' for c in 'hi there!'[:4]]
