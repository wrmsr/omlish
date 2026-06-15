"""
TODO:
 - better pipeline composition lol
"""
import abc
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish.http import all as http
from omlish.http import sse
from omlish.io.streams.framing import LongestMatchDelimiterByteStreamFrameDecoder
from omlish.io.streams.scanning import ScanningByteStreamBuffer
from omlish.io.streams.segmented import SegmentedByteStreamBuffer

from ..events.types import EventCallback
from ..resources import UseResources
from ..services import StreamResponse
from ..services import StreamResponseSink
from ..services import new_stream_response
from ..types import Option
from ..types import Output


##


@dc.dataclass()
@dc.extra_class_params(default_repr_fn=lang.opt_repr)
class HttpStreamResponseError(Exception):
    response: http.BaseHttpClientResponse

    data: lang.Bytes | None = None
    data_exception: Exception | None = None

    @classmethod
    async def from_response(cls, response: http.AsyncStreamHttpClientResponse) -> HttpStreamResponseError:
        data: lang.Bytes | None = None
        data_exception: Exception | None = None

        try:
            data = await response.stream.read()
        except Exception as de:  # noqa
            data_exception = de

        return HttpStreamResponseError(
            response,
            data=data,
            data_exception=data_exception,
        )


##


class HttpStreamResponseHandler(lang.Abstract):
    async def start(self) -> ta.Sequence[Output]:
        return ()

    @abc.abstractmethod
    async def finish(self) -> ta.Any:
        raise NotImplementedError


##


class BytesHttpStreamResponseHandler(HttpStreamResponseHandler, lang.Abstract):
    async def process_bytes(self, data: lang.Bytes) -> ta.Sequence[ta.Any]:
        return ()


class BytesHttpStreamResponseBuilder:
    def __init__(
            self,
            http_client: http.AsyncHttpClient | None,
            handling: ta.Callable[[http.AsyncStreamHttpClientResponse], BytesHttpStreamResponseHandler],
            *,
            read_chunk_size: int = -1,
            on_event: EventCallback | None = None,
    ) -> None:
        super().__init__()

        self._http_client = http_client
        self._handling = handling
        self._read_chunk_size = read_chunk_size
        self._on_event = on_event

    async def new_stream_response(
            self,
            http_request: http.HttpClientRequest,
            options: ta.Sequence[Option],
    ) -> StreamResponse:
        async with UseResources.or_new(options) as rs:
            http_client = await rs.enter_async_context(http.manage_async_client(self._http_client))
            http_response = await rs.enter_async_context(await http_client.stream_request(http_request))

            if http_response.status != 200:
                raise await HttpStreamResponseError.from_response(http_response)

            handler = self._handling(http_response)

            async def inner(sink: StreamResponseSink) -> ta.Any:
                while True:
                    b = await http_response.stream.read1(self._read_chunk_size)

                    for v in await handler.process_bytes(b):
                        if v is None:
                            break

                        await sink.emit(v)

                    if not b:
                        break

                return await handler.finish()

            return await new_stream_response(
                rs,
                inner,
                await handler.start(),
            )


##


class LinesHttpStreamResponseHandler(HttpStreamResponseHandler, lang.Abstract):
    async def process_line(self, line: lang.Bytes) -> ta.Sequence[ta.Any]:
        return ()

    def as_bytes(self) -> BytesHttpStreamResponseHandler:
        return LinesBytesHttpStreamResponseHandler(self)


class LinesBytesHttpStreamResponseHandler(BytesHttpStreamResponseHandler):
    def __init__(self, handler: LinesHttpStreamResponseHandler) -> None:
        super().__init__()

        self._handler = handler

        self._buf = ScanningByteStreamBuffer(SegmentedByteStreamBuffer(chunk_size=0x4000))
        self._frm = LongestMatchDelimiterByteStreamFrameDecoder([b'\r', b'\n', b'\r\n'])
        self._seen_eof = False

    async def start(self) -> ta.Sequence[Output]:
        return await self._handler.start()

    async def process_bytes(self, data: lang.Bytes) -> ta.Sequence[ta.Any]:
        check.state(not self._seen_eof)

        self._buf.write(data)

        out: list = []
        for o in self._frm.decode(self._buf, final=not data):
            for x in await self._handler.process_line(o.tobytes()):
                out.append(x)  # noqa

        if not data:
            self._seen_eof = True

            check.state(not len(self._buf))

        return out

    async def finish(self) -> ta.Any:
        check.state(self._seen_eof)

        return await self._handler.finish()


#


class SimpleLinesHttpStreamResponseHandler(LinesHttpStreamResponseHandler):
    def __init__(
            self,
            fn: ta.Callable[[lang.Bytes], ta.Awaitable[ta.Sequence[ta.Any]]],
            finish_fn: ta.Callable[[], ta.Awaitable[ta.Any]],
    ) -> None:
        super().__init__()

        self._fn = fn
        self._finish_fn = finish_fn

    async def process_line(self, line: lang.Bytes) -> ta.Sequence[ta.Any]:
        return await self._fn(line)

    async def finish(self) -> ta.Any:
        return await self._finish_fn()


##


class SseHttpStreamResponseHandler(HttpStreamResponseHandler, lang.Abstract):
    async def process_sse(self, so: sse.SseDecoderOutput) -> ta.Sequence[ta.Any]:
        return ()

    def as_lines(self) -> LinesHttpStreamResponseHandler:
        return SseLinesHttpStreamResponseHandler(self)


class SseLinesHttpStreamResponseHandler(LinesHttpStreamResponseHandler):
    def __init__(self, handler: SseHttpStreamResponseHandler) -> None:
        super().__init__()

        self._handler = handler

        self._sd = sse.SseDecoder()

    async def start(self) -> ta.Sequence[Output]:
        return await self._handler.start()

    async def process_line(self, line: lang.Bytes) -> ta.Sequence[ta.Any]:
        out: list[ta.Any] = []
        for so in self._sd.process_line(line):
            for x in await self._handler.process_sse(so):
                out.append(x)  # noqa
        return out

    async def finish(self) -> ta.Any:
        return await self._handler.finish()


#


class SimpleSseLinesHttpStreamResponseHandler(SseHttpStreamResponseHandler):
    def __init__(
            self,
            fn: ta.Callable[[sse.SseDecoderOutput], ta.Awaitable[ta.Sequence[ta.Any]]],
            finish_fn: ta.Callable[[], ta.Awaitable[ta.Any]],
    ) -> None:
        super().__init__()

        self._fn = fn
        self._finish_fn = finish_fn

    async def process_sse(self, so: sse.SseDecoderOutput) -> ta.Sequence[ta.Any]:
        return await self._fn(so)

    async def finish(self) -> ta.Any:
        return await self._finish_fn()
