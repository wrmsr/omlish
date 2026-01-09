import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish.http import all as http
from omlish.http import sse
from omlish.io.buffers import DelimitingBuffer

from ..resources import UseResources
from ..stream.services import StreamResponse
from ..stream.services import StreamResponseSink
from ..stream.services import new_stream_response
from ..types import Option
from ..types import Output


##


@dc.dataclass()
@dc.extra_class_params(default_repr_fn=lang.opt_repr)
class HttpStreamResponseError(Exception):
    response: http.BaseHttpResponse

    data: bytes | None = None
    data_exception: Exception | None = None

    @classmethod
    async def from_response(cls, response: http.AsyncStreamHttpResponse) -> 'HttpStreamResponseError':
        data: bytes | None = None
        data_exception: Exception | None = None

        try:
            data = await response.stream.readall()
        except Exception as de:  # noqa
            data_exception = de

        return HttpStreamResponseError(
            response,
            data=data,
            data_exception=data_exception,
        )


##


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
class SseHttpStreamResponseHandling(lang.Final):
    stream_outputs: ta.Sequence[Output] | None = None
    event_processor: ta.Callable[[sse.SseDecoderOutput], ta.Iterable | None] | None = None
    finalizer: ta.Callable[[], ta.Iterable[Output] | None] | None = None


async def new_sse_http_stream_response(
        http_client: http.AsyncHttpClient | None,
        http_request: http.HttpRequest,
        options: ta.Sequence[Option],
        handler: ta.Callable[[http.AsyncStreamHttpResponse], SseHttpStreamResponseHandling],
        *,
        read_chunk_size: int = -1,
) -> StreamResponse:
    async with UseResources.or_new(options) as rs:
        http_client = await rs.enter_async_context(http.manage_async_client(http_client))
        http_response = await rs.enter_async_context(await http_client.stream_request(http_request))

        if http_response.status != 200:
            raise await HttpStreamResponseError.from_response(http_response)

        handling = handler(http_response)

        async def inner(sink: StreamResponseSink) -> ta.Sequence | None:
            db = DelimitingBuffer([b'\r', b'\n', b'\r\n'])
            sd = sse.SseDecoder()

            while True:
                b = await http_response.stream.read1(read_chunk_size)

                for l in db.feed(b):
                    if isinstance(l, DelimitingBuffer.Incomplete):
                        # FIXME: handle
                        raise TypeError(l)

                    for so in sd.process_line(l):
                        if handling.event_processor is not None:
                            if (v_it := handling.event_processor(so)) is not None:
                                for v in v_it:
                                    await sink.emit(v)

                if not b:
                    break

            if handling.finalizer is None:
                return None

            return lang.opt_list(handling.finalizer())

        return await new_stream_response(
            rs,
            inner,
            handling.stream_outputs,
        )
