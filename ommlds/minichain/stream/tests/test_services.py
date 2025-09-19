import asyncio
import typing as ta

import pytest

from omlish import lang

from ...resources import UseResources
from ...services import Request
from ...types import Output
from ..services import StreamOptions
from ..services import StreamResponse
from ..services import StreamResponseSink
from ..services import new_stream_response


class FooStreamService:
    def __init__(self, *, do_sleep: bool) -> None:
        super().__init__()

        self.do_sleep = do_sleep
        self.num_sleeps = 0
        self.ran_finally = False

    async def invoke(self, request: Request[str, StreamOptions]) -> StreamResponse[str, Output, Output]:
        async with UseResources.or_new(request.options) as rs:
            async def inner(sink: StreamResponseSink[str]) -> ta.Sequence[Output] | None:
                try:
                    for c in request.v:
                        await sink.emit(c + '!')
                        if self.do_sleep:
                            await asyncio.sleep(.1)
                            self.num_sleeps += 1
                    return []
                finally:
                    if self.do_sleep:
                        await asyncio.sleep(.1)
                        self.num_sleeps += 1
                    self.ran_finally = True
            return await new_stream_response(rs, inner)


@pytest.mark.asyncs('asyncio')
async def test_foo_stream_service():
    lst: list = []
    async with (await (svc := FooStreamService(do_sleep=True)).invoke(Request('hi there!'))).v as it:
        async for e in it:
            lst.append(e)
    assert svc.num_sleeps == 10
    assert svc.ran_finally
    assert lst == [c + '!' for c in 'hi there!']


@pytest.mark.asyncs('asyncio')
async def test_foo_stream_service_break_early():
    lst: list = []
    async with (await (svc := FooStreamService(do_sleep=True)).invoke(Request('hi there!'))).v as it:
        for _ in range(4):
            lst.append(await it.__anext__())
    assert svc.num_sleeps == 4
    assert svc.ran_finally
    assert lst == [c + '!' for c in 'hi there!'[:4]]


def test_foo_stream_service_sync():
    svc = FooStreamService(do_sleep=False)
    req: Request = Request('hi there!')
    with lang.sync_async_with(lang.sync_await(svc.invoke(req)).v) as it:
        lst = lang.sync_async_list(it)
    assert svc.num_sleeps == 0
    assert svc.ran_finally
    assert lst == [c + '!' for c in 'hi there!']


def test_foo_stream_service_sync_break_early():
    svc = FooStreamService(do_sleep=False)
    req: Request = Request('hi there!')
    lst: list = []
    with lang.sync_async_with(lang.sync_await(svc.invoke(req)).v) as it:
        for _ in range(4):
            lst.append(lang.sync_await(it.__anext__()))
    assert svc.num_sleeps == 0
    assert svc.ran_finally
    assert lst == [c + '!' for c in 'hi there!'[:4]]
