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

from ...core import ChannelPipelineHandler
from ...core import ChannelPipelineHandlerContext
from ...core import ChannelPipelineMessages
from ..decoders import PipelineHttpContentChunkDecoder
from ..decoders import PipelineHttpDecoders
from ..decoders import PipelineHttpHeadDecoder
from ..requests import FullPipelineHttpRequest
from ..decoders import UntilEofPipelineHttpContentChunkDecoder
from ..decoders import ContentLengthPipelineHttpContentChunkDecoder
from ..decoders import ChunkedPipelineHttpContentChunkDecoder
from ..requests import PipelineHttpRequestAborted
from ..requests import PipelineHttpRequestContentChunk
from ..requests import PipelineHttpRequestEnd
from ..requests import PipelineHttpRequestHead


##


class PipelineHttpRequestHeadDecoder(ChannelPipelineHandler):
    """
    HTTP/1.x request head decoder.
    """

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
            max_head=max_head,
            buffer_chunk_size=buffer_chunk_size,
        )

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

        for dec_msg in self._decoder.inbound(
                msg,
                on_bytes_consumed=PipelineHttpDecoders.ctx_on_consumed_fn(ctx),
        ):
            ctx.feed_in(dec_msg)


##


class PipelineHttpRequestBodyAggregator(ChannelPipelineHandler):
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

    # @ta.override
    # def buffered_bytes(self) -> int:
    #     return len(self._buf)

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineMessages.Eof):
            # If we were expecting body bytes, that's a protocol error.
            if self._cur_head is not None and self._want and len(self._buf) < self._want:
                raise ValueError('EOF before HTTP request body complete')

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
        before = len(self._buf)
        body_view = self._buf.split_to(self._want)
        after = len(self._buf)

        if (bfc := ctx.bytes_flow_control) is not None:
            bfc.on_consumed(self, before - after)

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


class PipelineHttpRequestBodyStreamDecoder2(ChannelPipelineHandler):
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
            ctx.feed_in(msg)
            return

        if not isinstance(msg, PipelineHttpRequestHead):
            ctx.feed_in(msg)
            return

        sm = self._select_mode(msg)

        ctx.feed_in(msg)

        make_chunk = lambda data: PipelineHttpRequestContentChunk(data)  # noqa
        make_end = lambda: PipelineHttpRequestEnd()  # noqa

        if sm.mode == 'none':
            ctx.feed_in(PipelineHttpRequestEnd())

        elif sm.mode == 'eof':
            self._decoder = UntilEofPipelineHttpContentChunkDecoder(
                make_chunk,
                make_end,
            )

        elif sm.mode == 'cl':
            self._decoder = ContentLengthPipelineHttpContentChunkDecoder(
                make_chunk,
                make_end,
                sm.length,
            )

        elif sm.mode == 'chunked':
            self._decoder = ChunkedPipelineHttpContentChunkDecoder(
                make_chunk,
                make_end,
                max_chunk_header=self._max_chunk_header,
            )

        else:
            raise RuntimeError(f'unexpected mode {sm!r}')


##


_PipelineHttpRequestBodyStreamDecoderMode = ta.Literal[  # ta.TypeAlias  # omlish-amalg-typing-no-move
    'none',
    'cl',
    'chunked',
    'eof',
]


class PipelineHttpRequestBodyStreamDecoder(ChannelPipelineHandler):
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
            max_buffer: ta.Optional[int] = 0x400000,
            buffer_chunk_size: int = 0x10000,
    ) -> None:
        super().__init__()

        self._max_chunk = max_chunk

        self._buf = SegmentedByteStreamBuffer(
            max_bytes=max_buffer,
            chunk_size=buffer_chunk_size,
        )

        self._head: ta.Optional[PipelineHttpRequestHead] = None
        self._mode: ta.Optional[_PipelineHttpRequestBodyStreamDecoderMode] = None
        self._remain = 0

        # chunked parsing state (follows PipelineHttpChunkedDecoder pattern)
        self._chunk_remain: ta.Optional[int] = None  # None -> need size line; 0 -> need trailers/end
        self._chunk_state: ta.Literal['size', 'data', 'trailer'] = 'size'

    # @ta.override
    # def buffered_bytes(self) -> int:
    #     return len(self._buf)

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineMessages.Eof):
            # EOF: if we're in eof-mode, this terminates body; otherwise abort if incomplete.
            if self._head is None:
                ctx.feed_in(msg)
                return

            if self._mode == 'eof':
                ctx.feed_in(PipelineHttpRequestEnd())
            else:
                # Abort if we were expecting more bytes.
                if self._mode == 'cl' and self._remain != 0:
                    ctx.feed_in(PipelineHttpRequestAborted('EOF before Content-Length satisfied'))
                elif self._mode == 'chunked' and self._chunk_remain != 0:
                    ctx.feed_in(PipelineHttpRequestAborted('EOF before chunked body complete'))
                else:
                    # mode == 'none' or already complete
                    ctx.feed_in(PipelineHttpRequestEnd())

            # Reset state for next request (we don't support pipelining, but keep it tidy)
            self._reset()
            ctx.feed_in(msg)
            return

        if isinstance(msg, PipelineHttpRequestHead):
            if self._head is not None:
                raise ValueError('HTTP pipelining not supported')

            self._head = msg
            self._mode, self._remain, self._chunk_remain = self._select_mode(msg)

            ctx.feed_in(msg)

            # If no body expected, end immediately.
            if self._mode == 'none':
                ctx.feed_in(PipelineHttpRequestEnd())
                self._reset()
            return

        if not ByteStreamBuffers.can_bytes(msg):
            ctx.feed_in(msg)
            return

        # Body bytes-like
        if self._head is None:
            # Ignore stray bytes; decoder not armed yet.
            return

        before = len(self._buf)

        added = 0
        for mv in ByteStreamBuffers.iter_segments(msg):
            if mv:
                added += len(mv)
                self._buf.write(mv)

        if self._mode == 'cl':
            self._drain_content_length(ctx)
        elif self._mode == 'chunked':
            self._drain_chunked(ctx)
        elif self._mode == 'eof':
            self._drain_until_eof(ctx)
        else:
            # none: shouldn't be receiving bytes
            pass

        after = len(self._buf)

        # Flow-control refund must be the number of bytes removed from our internal buffer. We added `added` bytes, and
        # our internal buffer grew by (after - before).
        removed = before + added - after
        if removed > 0:
            if (bfc := ctx.bytes_flow_control) is not None:
                bfc.on_consumed(self, removed)

    class _SelectedMode(ta.NamedTuple):
        mode: _PipelineHttpRequestBodyStreamDecoderMode
        remain: int
        chunk_remain: ta.Optional[int]

    def _select_mode(self, head: PipelineHttpRequestHead) -> _SelectedMode:
        if head.headers.contains_value('transfer-encoding', 'chunked', ignore_case=True):
            return PipelineHttpRequestBodyStreamDecoder._SelectedMode('chunked', 0, None)

        cl = head.headers.single.get('content-length')
        if cl is not None and cl != '':
            try:
                n = int(cl)
            except ValueError:
                raise ValueError('bad Content-Length') from None

            if n < 0:
                raise ValueError('bad Content-Length')

            if n == 0:
                return PipelineHttpRequestBodyStreamDecoder._SelectedMode('none', 0, 0)

            return PipelineHttpRequestBodyStreamDecoder._SelectedMode('cl', n, 0)

        # No length info: treat as until EOF (supports infinite streaming).
        return PipelineHttpRequestBodyStreamDecoder._SelectedMode('eof', 0, 0)

    def _drain_content_length(self, ctx: ChannelPipelineHandlerContext) -> int:
        # Emit as many chunks as available up to remaining length.
        while self._remain and len(self._buf):
            take = self._remain
            if take > len(self._buf):
                take = len(self._buf)
            if take > self._max_chunk:
                take = self._max_chunk

            v = self._buf.split_to(take)
            data = v.tobytes()
            ctx.feed_in(PipelineHttpRequestContentChunk(data))
            self._remain -= take

        if self._remain == 0:
            ctx.feed_in(PipelineHttpRequestEnd())
            self._reset()

        return 0

    def _drain_until_eof(self, ctx: ChannelPipelineHandlerContext) -> int:
        # Emit whatever is available as chunks; never terminates except on EOF event.
        while len(self._buf):
            take = len(self._buf)
            if take > self._max_chunk:
                take = self._max_chunk
            v = self._buf.split_to(take)
            ctx.feed_in(PipelineHttpRequestContentChunk(v.tobytes()))
        return 0

    def _drain_chunked(self, ctx: ChannelPipelineHandlerContext) -> int:
        """
        RFC 7230 chunked decoding. Follows PipelineHttpChunkedDecoder pattern.

        Note: Flow control is handled at the higher inbound() level via buffer size tracking, unlike
        PipelineHttpChunkedDecoder which tracks per-operation.
        """

        while True:
            if self._chunk_state == 'size':
                # Parse chunk size line: <hex-size>\r\n
                i = self._buf.find(b'\r\n')
                if i < 0:
                    return 0

                line = self._buf.split_to(i).tobytes()
                self._buf.advance(2)  # CRLF
                s = line.split(b';', 1)[0].strip()
                try:
                    n = int(s, 16)
                except ValueError:
                    raise ValueError('Invalid chunk size') from None
                if n < 0:
                    raise ValueError('Invalid chunk size')

                self._chunk_remain = n
                if n == 0:
                    # Final chunk
                    self._chunk_state = 'trailer'
                else:
                    self._chunk_state = 'data'
                continue

            elif self._chunk_state == 'data':
                # Read chunk data + trailing \r\n
                if len(self._buf) < check.not_none(self._chunk_remain) + 2:
                    return 0

                data_v = self._buf.split_to(check.not_none(self._chunk_remain))
                data = data_v.tobytes()

                # Verify trailing \r\n
                trailing = self._buf.split_to(2)
                trailing_bytes = trailing.tobytes()
                if trailing_bytes != b'\r\n':
                    raise ValueError(f'Expected \\r\\n after chunk data, got {trailing_bytes!r}')

                ctx.feed_in(PipelineHttpRequestContentChunk(data))
                self._chunk_remain = None
                self._chunk_state = 'size'

            elif self._chunk_state == 'trailer':
                # Final \r\n after 0-size chunk (or \r\n\r\n with trailers)
                # Tolerate both \r\n\r\n (with trailers) and \r\n (no trailers)
                j = self._buf.find(b'\r\n\r\n')
                if j >= 0:
                    self._buf.advance(j + 4)
                    ctx.feed_in(PipelineHttpRequestEnd())
                    self._reset()
                    return 0

                # Simple case: just \r\n
                if len(self._buf) >= 2 and self._buf.find(b'\r\n', 0, 2) == 0:
                    self._buf.advance(2)
                    ctx.feed_in(PipelineHttpRequestEnd())
                    self._reset()
                    return 0

                return 0

        raise RuntimeError('unreachable')

    def _reset(self) -> None:
        self._head = None
        self._mode = None
        self._remain = 0
        self._chunk_remain = None
        self._chunk_state = 'size'
        # leave _buf empty; any leftover bytes would imply pipelining, which we currently reject
        if len(self._buf):
            # treat as protocol error
            raise ValueError('unexpected extra bytes after request')
