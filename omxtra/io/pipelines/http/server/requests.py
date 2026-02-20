# ruff: noqa: UP045
# @omlish-lite
import typing as ta

from omlish.http.headers import HttpHeaders
from omlish.http.parsing import HttpParser
from omlish.http.parsing import ParsedHttpMessage
from omlish.io.streams.errors import FrameTooLargeByteStreamBufferError
from omlish.io.streams.segmented import SegmentedByteStreamBuffer
from omlish.io.streams.utils import ByteStreamBuffers
from omlish.lite.check import check

from ...bytes.buffering import InboundBytesBufferingChannelPipelineHandler
from ...core import ChannelPipelineHandlerContext
from ...core import ChannelPipelineMessages
from ..decoders import ChunkedPipelineHttpContentChunkDecoder
from ..decoders import ContentLengthPipelineHttpContentChunkDecoder
from ..decoders import PipelineHttpContentChunkDecoder
from ..decoders import PipelineHttpHeadDecoder
from ..decoders import UntilFinalInputPipelineHttpContentChunkDecoder
from ..requests import FullPipelineHttpRequest
from ..requests import PipelineHttpRequestAborted
from ..requests import PipelineHttpRequestContentChunk
from ..requests import PipelineHttpRequestEnd
from ..requests import PipelineHttpRequestHead


##


class PipelineHttpRequestHeadDecoder(InboundBytesBufferingChannelPipelineHandler):
    """HTTP/1.x request head decoder."""

    def __init__(
            self,
            *,
            max_head: int = 0x10000,
            buffer_chunk_size: int = 0x10000,
    ) -> None:
        super().__init__()

        self._decoder = PipelineHttpHeadDecoder(
            HttpParser.Mode.REQUEST,
            lambda parsed: self._build_head(parsed),
            lambda reason: PipelineHttpRequestAborted(reason),
            max_head=max_head,
            buffer_chunk_size=buffer_chunk_size,
        )

    def inbound_buffered_bytes(self) -> int:
        return self._decoder.inbound_buffered_bytes()

    def _build_head(self, parsed: ParsedHttpMessage) -> PipelineHttpRequestHead:
        line = check.not_none(parsed.request_line)

        return PipelineHttpRequestHead(
            method=line.method,
            target=check.not_none(line.request_target).decode('utf-8'),
            version=line.http_version,
            headers=HttpHeaders(parsed.headers.entries),
            parsed=parsed,
        )

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if self._decoder.done:
            ctx.feed_in(msg)
            return

        for dec_msg in self._decoder.inbound(msg):
            ctx.feed_in(dec_msg)


##


class PipelineHttpRequestBodyAggregator(InboundBytesBufferingChannelPipelineHandler):
    """
    Aggregates an HTTP/1 request body using Content-Length.

    Input:
      - DecodedHttpRequestHead (from HttpRequestDecoder)
      - subsequent bytes-like chunks / views (body bytes)

    Output:
      - FullPipelineHttpRequest(head, body)

    Notes:
      - This is intentionally minimal:
        - Only supports Content-Length
        - No chunked transfer decoding
        - Assumes one request per connection in our server examples (we close after response)
      - Body bytes may arrive in the same TCP read as the head; HttpRequestDecoder forwards any remainder.

    TODO:
      - Use ContentLengthPipelineHttpContentChunkDecoder
    """

    def __init__(
            self,
            *,
            max_body: ta.Optional[int] = 0x100000,
            buffer_chunk_size: int = 0x10000,
    ) -> None:
        super().__init__()

        self._max_body = max_body

        self._cur_head: ta.Optional[PipelineHttpRequestHead] = None
        self._want = 0
        self._buf = SegmentedByteStreamBuffer(
            max_bytes=self._max_body,
            chunk_size=buffer_chunk_size,
        )

    def inbound_buffered_bytes(self) -> int:
        return len(self._buf)

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineMessages.FinalInput):
            # If we were expecting body bytes, that's a protocol error.
            if self._cur_head is not None and self._want and len(self._buf) < self._want:
                ctx.feed_in(PipelineHttpRequestAborted('EOF before HTTP request body complete'))

                self._cur_head = None
                self._want = 0
                self._buf.split_to(len(self._buf))

            ctx.feed_in(msg)
            return

        if isinstance(msg, PipelineHttpRequestHead):
            if self._cur_head is not None:
                # We don't support pipelining in this minimal server.
                raise ValueError('HTTP pipelining not supported')

            self._cur_head = msg

            cl = msg.headers.single.get('content-length')
            if cl is None or cl == '':
                self._want = 0

            else:
                try:
                    self._want = int(cl)
                except ValueError:
                    raise ValueError('bad Content-Length') from None

                if self._want < 0:
                    raise ValueError('bad Content-Length')

                if self._max_body is not None and self._want > self._max_body:
                    raise FrameTooLargeByteStreamBufferError('request body exceeded max_body')

            if self._want == 0:
                req = FullPipelineHttpRequest(msg, b'')
                self._cur_head = None
                self._want = 0
                ctx.feed_in(req)

            return

        if not ByteStreamBuffers.can_bytes(msg):
            ctx.feed_in(msg)
            return

        # Body bytes
        if self._cur_head is None:
            # Ignore stray bytes (or treat as error). Minimal server: ignore.
            return

        for mv in ByteStreamBuffers.iter_segments(msg):
            if mv:
                self._buf.write(mv)

        # If still not enough, just wait.
        if len(self._buf) < self._want:
            return

        # Extract exactly want bytes; preserve any extra (we don't support pipelining, but be correct).
        body_view = self._buf.split_to(self._want)
        body = body_view.tobytes()

        head = self._cur_head
        self._cur_head = None
        self._want = 0

        req = FullPipelineHttpRequest(head, body)
        ctx.feed_in(req)

        # If leftover bytes exist, treat as protocol error in our minimal server model.
        if len(self._buf):
            raise ValueError('unexpected extra bytes after request body')


##


class PipelineHttpRequestBodyStreamDecoder(InboundBytesBufferingChannelPipelineHandler):
    """
    Turns (PipelineHttpRequestHead + subsequent bytes) into streaming PipelineHttpContentChunk events +
    PipelineHttpRequestEnd.

    Supported body modes:
      - Content-Length: reads exactly that many bytes
      - Transfer-Encoding: chunked: decodes RFC 7230 chunked encoding (minimal, trailers ignored beyond terminator)
      - Neither present: treats body as "until EOF" (useful for infinite streaming uploads)
    """

    def __init__(
            self,
            *,
            max_chunk: int = 0x100000,
            max_chunk_header: int = 1024,
            buffer_chunk_size: int = 0x10000,
    ) -> None:
        super().__init__()

        self._max_chunk = max_chunk
        self._max_chunk_header = max_chunk_header
        self._buffer_chunk_size = buffer_chunk_size

        self._decoder: ta.Optional[PipelineHttpContentChunkDecoder] = None

    def inbound_buffered_bytes(self) -> int:
        if (dec := self._decoder) is None:
            return 0
        return dec.inbound_buffered_bytes()

    class _SelectedMode(ta.NamedTuple):
        mode: ta.Literal['none', 'eof', 'cl', 'chunked']
        length: ta.Optional[int]

    def _select_mode(self, head: PipelineHttpRequestHead) -> _SelectedMode:
        if head.headers.contains_value('transfer-encoding', 'chunked', ignore_case=True):
            return self._SelectedMode('chunked', None)

        cl = head.headers.single.get('content-length')
        if cl is not None and cl != '':
            try:
                n = int(cl)
            except ValueError:
                raise ValueError('bad Content-Length') from None

            if n < 0:
                raise ValueError('bad Content-Length')

            if n == 0:
                return self._SelectedMode('none', None)

            return self._SelectedMode('cl', n)

        # No length info: treat as until EOF (supports infinite streaming).
        return self._SelectedMode('eof', None)

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if self._decoder is not None:
            if self._decoder.done:
                ctx.feed_in(msg)
                return

            for dec_msg in self._decoder.inbound(msg):
                ctx.feed_in(dec_msg)

            return

        if not isinstance(msg, PipelineHttpRequestHead):
            ctx.feed_in(msg)
            return

        sm = self._select_mode(msg)

        ctx.feed_in(msg)

        make_chunk = lambda data: PipelineHttpRequestContentChunk(data)  # noqa
        make_end = lambda: PipelineHttpRequestEnd()  # noqa
        make_aborted = lambda reason: PipelineHttpRequestAborted(reason)  # noqa

        if sm.mode == 'none':
            ctx.feed_in(PipelineHttpRequestEnd())

        elif sm.mode == 'eof':
            self._decoder = UntilFinalInputPipelineHttpContentChunkDecoder(
                make_chunk,
                make_end,
                make_aborted,
            )

        elif sm.mode == 'cl':
            self._decoder = ContentLengthPipelineHttpContentChunkDecoder(
                make_chunk,
                make_end,
                make_aborted,
                check.not_none(sm.length),
            )

        elif sm.mode == 'chunked':
            self._decoder = ChunkedPipelineHttpContentChunkDecoder(
                make_chunk,
                make_end,
                make_aborted,
                max_chunk_header=self._max_chunk_header,
            )

        else:
            raise RuntimeError(f'unexpected mode {sm!r}')
