"""
TODO:
 - better pipeline composition lol
"""
import typing as ta

from omlish import check
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


class HttpStreamResponseHandler(lang.Abstract):
    def start(self) -> ta.Sequence[Output]:
        return ()

    def finish(self) -> ta.Sequence[Output]:
        return ()


##


class BytesHttpStreamResponseHandler(HttpStreamResponseHandler, lang.Abstract):
    def process_bytes(self, data: bytes) -> ta.Iterable:
        return ()


class BytesHttpStreamResponseBuilder:
    def __init__(
            self,
            http_client: http.AsyncHttpClient | None,
            handling: ta.Callable[[http.AsyncStreamHttpResponse], BytesHttpStreamResponseHandler],
            *,
            read_chunk_size: int = -1,
    ) -> None:
        super().__init__()

        self._http_client = http_client
        self._handling = handling
        self._read_chunk_size = read_chunk_size

    async def new_stream_response(
            self,
            http_request: http.HttpRequest,
            options: ta.Sequence[Option],
    ) -> StreamResponse:
        async with UseResources.or_new(options) as rs:
            http_client = await rs.enter_async_context(http.manage_async_client(self._http_client))
            http_response = await rs.enter_async_context(await http_client.stream_request(http_request))

            if http_response.status != 200:
                raise await HttpStreamResponseError.from_response(http_response)

            handler = self._handling(http_response)

            async def inner(sink: StreamResponseSink) -> ta.Sequence | None:
                while True:
                    b = await http_response.stream.read1(self._read_chunk_size)

                    for v in handler.process_bytes(b):
                        if v is None:
                            break

                        await sink.emit(v)

                    if not b:
                        break

                return handler.finish()

            return await new_stream_response(
                rs,
                inner,
                handler.start(),
            )


##


class LinesHttpStreamResponseHandler(HttpStreamResponseHandler, lang.Abstract):
    def process_line(self, line: bytes) -> ta.Iterable:
        return ()

    def as_bytes(self) -> BytesHttpStreamResponseHandler:
        return LinesBytesHttpStreamResponseHandler(self)


class LinesBytesHttpStreamResponseHandler(BytesHttpStreamResponseHandler):
    def __init__(self, handler: LinesHttpStreamResponseHandler) -> None:
        super().__init__()

        self._handler = handler

        self._db = DelimitingBuffer([b'\r', b'\n', b'\r\n'])

    def start(self) -> ta.Sequence[Output]:
        return self._handler.start()

    def process_bytes(self, data: bytes) -> ta.Iterable:
        for o in self._db.feed(data):
            if isinstance(o, bytes):
                yield from self._handler.process_line(o)

            else:
                raise TypeError(o)

    def finish(self) -> ta.Sequence[Output]:
        check.state(self._db.is_closed)

        return self._handler.finish()


##


class SseHttpStreamResponseHandler(HttpStreamResponseHandler, lang.Abstract):
    def process_sse(self, so: sse.SseDecoderOutput) -> ta.Iterable:
        return ()

    def as_lines(self) -> LinesHttpStreamResponseHandler:
        return SseLinesHttpStreamResponseHandler(self)


class SseLinesHttpStreamResponseHandler(LinesHttpStreamResponseHandler):
    def __init__(self, handler: SseHttpStreamResponseHandler) -> None:
        super().__init__()

        self._handler = handler

        self._sd = sse.SseDecoder()

    def start(self) -> ta.Sequence[Output]:
        return self._handler.start()

    def process_line(self, line: bytes) -> ta.Iterable:
        for so in self._sd.process_line(line):
            yield from self._handler.process_sse(so)

    def finish(self) -> ta.Sequence[Output]:
        return self._handler.finish()


#


class SimpleSseLinesHttpStreamResponseHandler(SseHttpStreamResponseHandler):
    def __init__(self, fn: ta.Callable[[sse.SseDecoderOutput], ta.Iterable]) -> None:
        super().__init__()

        self._fn = fn

    def process_sse(self, so: sse.SseDecoderOutput) -> ta.Iterable:
        return self._fn(so)
