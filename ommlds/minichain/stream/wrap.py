# ruff: noqa: UP028
import typing as ta

from ..resources import Resources
from ..services import Request
from ..services import Service
from ..types import Output
from .services import ResponseGenerator
from .services import StreamResponse
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

    def _process_request(self, request: StreamRequestT) -> StreamRequestT:
        return request

    def _process_stream_outputs(self, outputs: ta.Sequence[StreamOutputT]) -> ta.Sequence[StreamOutputT]:
        return outputs

    def _process_vs(self, vs: ta.Iterator[V]) -> ta.Iterator[V]:
        return vs

    def _process_outputs(self, outputs: ta.Sequence[OutputT]) -> ta.Sequence[OutputT]:
        return outputs

    #

    def invoke(self, request: StreamRequestT) -> StreamResponse[V, OutputT, StreamOutputT]:
        with Resources.new() as rs:
            in_response = self._inner.invoke(self._process_request(request))
            in_vs: ResponseGenerator[V, OutputT] = rs.enter_context(in_response.v)
            out_vs = self._process_vs(in_vs)

            def yield_vs() -> ta.Generator[V, None, ta.Sequence[OutputT] | None]:
                while True:
                    try:
                        out_v = next(out_vs)
                    except StopIteration as se:
                        return self._process_outputs(se.value)
                    yield out_v

            return new_stream_response(
                rs,
                yield_vs(),
                self._process_stream_outputs(in_response.outputs),
            )
