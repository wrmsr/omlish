# ruff: noqa: UP028
import typing as ta

from ..resources import Resources
from ..services import Request
from ..services import Service
from ..types import Output
from .services import StreamResponseIterator
from .services import StreamResponse
from .services import StreamResponseSink
from .services import new_stream_response


StreamRequestT = ta.TypeVar('StreamRequestT', bound=Request)
V = ta.TypeVar('V')
OutputT = ta.TypeVar('OutputT', bound=Output)
StreamOutputT = ta.TypeVar('StreamOutputT', bound=Output)


##


class WrappedStreamService(ta.Generic[StreamRequestT, V, OutputT, StreamOutputT]):
    """Only handles simple, non-type-modifying usecases."""

    def __init__(self, inner: Service[StreamRequestT, StreamResponse[V, OutputT, StreamOutputT]]) -> None:
        super().__init__()

        self._inner = inner

    #

    async def _process_request(self, request: StreamRequestT) -> StreamRequestT:
        return request

    async def _process_stream_outputs(self, outputs: ta.Sequence[StreamOutputT]) -> ta.Sequence[StreamOutputT]:
        return outputs

    async def _process_value(self, v: V) -> ta.Iterable[V]:
        return [v]

    async def _process_outputs(self, outputs: ta.Sequence[OutputT]) -> ta.Sequence[OutputT]:
        return outputs

    #

    async def invoke(self, request: StreamRequestT) -> StreamResponse[V, OutputT, StreamOutputT]:
        async with Resources.new() as rs:
            in_resp = await self._inner.invoke(await self._process_request(request))
            in_vs = await rs.enter_async_context(in_resp.v)

            def inner(sink: StreamResponseSink) -> ta.Generator[V, None, ta.Sequence[OutputT] | None]:
                while True:
                    try:
                        out_v = next(out_vs)
                    except StopIteration as se:
                        return self._process_outputs(se.value)
                    yield out_v

            return new_stream_response(
                rs,
                yield_vs(),
                self._process_stream_outputs(in_resp.outputs),
            )
