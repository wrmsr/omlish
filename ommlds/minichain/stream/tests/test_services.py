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
    async def invoke(self, request: Request[str, StreamOptions]) -> StreamResponse[str, Output, Output]:
        async with UseResources.or_new(request.options) as rs:
            async def inner(sink: StreamResponseSink[str]) -> ta.Sequence[Output] | None:
                for c in request.v:
                    await sink.emit(c + '!')
                return []
            return await new_stream_response(rs, inner)


@pytest.mark.asyncs('asyncio')
async def test_foo_stream_service():
    lst: list = []
    async with (await FooStreamService().invoke(Request('hi there!'))).v as it:
        async for e in it:
            lst.append(e)
    assert lst == [c + '!' for c in 'hi there!']


def test_foo_stream_service_sync():
    svc = FooStreamService()
    req: Request = Request('hi there!')
    with lang.sync_await_context_manager(lang.sync_await(svc.invoke(req)).v) as it:
        lst = lang.sync_async_list(it)
    assert lst == [c + '!' for c in 'hi there!']
