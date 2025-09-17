import typing as ta

import pytest

from omlish import lang

from ...resources import UseResources
from ...services import Request
from ...types import Output
from ..services import StreamOptions
from ..services import StreamResponse
from ..services import new_stream_response


class FooStreamService:
    async def invoke(self, request: Request[str, StreamOptions]) -> StreamResponse[str, Output, Output]:
        async with UseResources.or_new(request.options) as rs:
            @lang.async_generator_with_return
            async def yield_vs(set_value):
                for c in request.v:
                    yield c + '!'
                set_value(None)
            return await new_stream_response(rs, yield_vs())


@pytest.mark.asyncs('asyncio')
async def test_foo_stream_service():
    async with (await FooStreamService().invoke(Request('hi there!'))).v as it:
        lst = await lang.async_list(it)
    assert lst == [c + '!' for c in 'hi there!']


def test_foo_stream_service_sync():
    svc = FooStreamService()
    req = Request('hi there!')
    with lang.sync_await_context_manager(lang.sync_await(svc.invoke(req)).v) as it:
        lst = lang.sync_async_list(it)
    assert lst == [c + '!' for c in 'hi there!']
