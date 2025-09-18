# ruff: noqa: UP028
import typing as ta

from ..resources import UseResources
from ..services import Request
from ..services import Service
from ..types import Output
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
        async with UseResources.or_new(request.options) as rs:  # noqa
            in_resp = await self._inner.invoke(await self._process_request(request))
            in_vs = await rs.enter_async_context(in_resp.v)

            async def inner(sink: StreamResponseSink[V]) -> ta.Sequence[OutputT] | None:
                async for in_v in in_vs:
                    for out_v in (await self._process_value(in_v)):
                        await sink.emit(out_v)

                return await self._process_outputs(in_vs.outputs)

            return await new_stream_response(
                rs,
                inner,
                await self._process_stream_outputs(in_resp.outputs),
            )
