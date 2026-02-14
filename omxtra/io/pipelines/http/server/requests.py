# ruff: noqa: UP045
# @omlish-lite
import typing as ta

from omlish.http.headers import HttpHeaders
from omlish.http.parsing import HttpParser
from omlish.http.parsing import parse_http_message
from omlish.io.streams.errors import FrameTooLargeByteStreamBufferError
from omlish.io.streams.segmented import SegmentedByteStreamBuffer
from omlish.io.streams.utils import ByteStreamBuffers
from omlish.lite.check import check

from ...core import ChannelPipelineEvents
from ...core import ChannelPipelineHandler
from ...core import ChannelPipelineHandlerContext
from ..requests import FullPipelineHttpRequest
from ..requests import PipelineHttpContentChunk
from ..requests import PipelineHttpRequestAborted
from ..requests import PipelineHttpRequestEnd
from ..requests import PipelineHttpRequestHead


##


class PipelineHttpRequestHeadDecoder(ChannelPipelineHandler):
    """
    Minimal HTTP/1.x request head decoder (demo-grade).

    Inbound:
      - buffers until b'\\r\\n\\r\\n'
      - parses request line + headers
      - emits DecodedHttpRequestHead
      - forwards any remaining bytes (ignored by ping example)

    Not supported:
      - request bodies
      - chunked encoding
      - pipelining / keep-alive correctness beyond the demo
    """

    def __init__(
            self,
            *,
            max_head: int = 0x10000,
            chunk_size: int = 0x10000,
    ) -> None:
        super().__init__()

        self._max_head = max_head

        self._buf = SegmentedByteStreamBuffer(
            max_bytes=max_head,
            chunk_size=chunk_size,
        )
        self._passthrough_body = False

    # @ta.override
    # def buffered_bytes(self) -> int:
    #     return len(self._buf)

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineEvents.Eof):
            # EOF: if we have partial head buffered and we haven't switched to body passthrough, that's an error.
            if not self._passthrough_body and len(self._buf):
                raise ValueError('EOF before HTTP request head complete')

            # Either way, reset.
            self._passthrough_body = False
            if len(self._buf):
                _ = self._buf.split_to(len(self._buf))

            ctx.feed_in(msg)
            return

        # If we've already parsed the request head, we are in "body passthrough" mode: forward bytes-like directly
        # downstream without further head parsing.
        if self._passthrough_body:
            ctx.feed_in(msg)
            return

        if not ByteStreamBuffers.can_bytes(msg):
            ctx.feed_in(msg)
            return

        before = len(self._buf)

        for mv in ByteStreamBuffers.iter_segments(msg):
            if mv:
                self._buf.write(mv)

        i = self._buf.find(b'\r\n\r\n')
        if i < 0:
            return

        head_view = self._buf.split_to(i + 4)

        after = len(self._buf)

        if (bfc := ctx.bytes_flow_control) is not None:
            bfc.on_consumed(before - after + (i + 4))

        req = self._parse_head(ByteStreamBuffers.to_bytes(head_view))
        ctx.feed_in(req)

        # Switch into body passthrough mode after emitting the head.
        self._passthrough_body = True

        # Forward any remainder bytes that were read alongside the head (body bytes).
        if len(self._buf):
            rem = len(self._buf)
            rem_view = self._buf.split_to(rem)

            ctx.feed_in(rem_view)

    def _parse_head(self, raw: bytes) -> PipelineHttpRequestHead:
        parsed = parse_http_message(raw, mode=HttpParser.Mode.REQUEST)
        line = check.not_none(parsed.request_line)

        return PipelineHttpRequestHead(
            method=line.method,
            target=check.not_none(line.request_target).decode('utf-8'),
            version=line.http_version,
            headers=HttpHeaders(parsed.headers.entries),
            parsed=parsed,
        )


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
            chunk_size: int = 0x10000,
    ) -> None:
        super().__init__()

        self._max_body = max_body

        self._cur_head: ta.Optional[PipelineHttpRequestHead] = None
        self._want = 0
        self._buf = SegmentedByteStreamBuffer(
            max_bytes=self._max_body,
            chunk_size=chunk_size,
        )

    # @ta.override
    # def buffered_bytes(self) -> int:
    #     return len(self._buf)

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineEvents.Eof):
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

        before = len(self._buf)

        for mv in ByteStreamBuffers.iter_segments(msg):
            if mv:
                self._buf.write(mv)

        # If still not enough, just wait.
        if len(self._buf) < self._want:
            return

        # Extract exactly want bytes; preserve any extra (we don't support pipelining, but be correct).
        body_view = self._buf.split_to(self._want)
        after = len(self._buf)

        if (bfc := ctx.bytes_flow_control) is not None:
            bfc.on_consumed(before - after + self._want)

        body = ByteStreamBuffers.to_bytes(body_view)

        head = self._cur_head
        self._cur_head = None
        self._want = 0

        req = FullPipelineHttpRequest(head, body)
        ctx.feed_in(req)

        # If leftover bytes exist, treat as protocol error in our minimal server model.
        if len(self._buf):
            raise ValueError('unexpected extra bytes after request body')


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

    This keeps the "simple non-streaming body" path possible via a separate aggregator handler:
      PipelineHttpRequestHead -> PipelineHttpContentChunk* -> PipelineHttpRequestEnd (stream)
      PipelineHttpRequestHead -> FullPipelineHttpRequest(head, body) (aggregated)
    """

    def __init__(
            self,
            *,
            max_chunk: int = 0x100000,
            max_buf: ta.Optional[int] = 0x400000,
            chunk_size: int = 0x10000,
    ) -> None:
        super().__init__()

        self._max_chunk = max_chunk

        self._buf = SegmentedByteStreamBuffer(
            max_bytes=max_buf,
            chunk_size=chunk_size,
        )

        self._head: ta.Optional[PipelineHttpRequestHead] = None
        self._mode: ta.Optional[_PipelineHttpRequestBodyStreamDecoderMode] = None
        self._remain = 0

        # chunked parsing state
        self._chunk_remain: ta.Optional[int] = None  # None -> need size line; 0 -> need trailers/end

    # @ta.override
    # def buffered_bytes(self) -> int:
    #     return len(self._buf)

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineEvents.Eof):
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
                bfc.on_consumed(removed)

    class _SelectedMode(ta.NamedTuple):
        mode: _PipelineHttpRequestBodyStreamDecoderMode
        remain: int
        chunk_remain: ta.Optional[int]

    def _select_mode(self, head: PipelineHttpRequestHead) -> _SelectedMode:
        te = head.headers.lower.get('transfer-encoding', '')
        if 'chunked' in te:
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
            data = ByteStreamBuffers.to_bytes(v)
            ctx.feed_in(PipelineHttpContentChunk(data))
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
            ctx.feed_in(PipelineHttpContentChunk(ByteStreamBuffers.to_bytes(v)))
        return 0

    def _drain_chunked(self, ctx: ChannelPipelineHandlerContext) -> int:
        # Minimal RFC 7230 chunked decoding:
        # chunk-size (hex) [;ext] CRLF
        # chunk-data CRLF
        # ...
        # 0 CRLF
        # trailers CRLF
        # CRLF
        while True:
            if self._chunk_remain is None:
                # Need a size line.
                i = self._buf.find(b'\r\n')
                if i < 0:
                    return 0
                line = ByteStreamBuffers.to_bytes(self._buf.split_to(i))
                self._buf.advance(2)  # CRLF
                s = line.split(b';', 1)[0].strip()
                try:
                    n = int(s, 16)
                except ValueError:
                    raise ValueError('bad chunk size') from None
                if n < 0:
                    raise ValueError('bad chunk size')
                self._chunk_remain = n
                if n == 0:
                    # Need terminator trailers: consume through \r\n\r\n if present.
                    self._chunk_remain = 0
                continue

            if self._chunk_remain == 0:
                # Consume trailers terminator: require \r\n\r\n (empty trailers) or tolerate simple \r\n.
                j = self._buf.find(b'\r\n\r\n')
                if j >= 0:
                    self._buf.advance(j + 4)
                    ctx.feed_in(PipelineHttpRequestEnd())
                    self._reset()
                    return 0
                # If not found, we might only have '\r\n' for no trailers in some cases.
                if len(self._buf) >= 2 and self._buf.find(b'\r\n', 0, 2) == 0:
                    self._buf.advance(2)
                    ctx.feed_in(PipelineHttpRequestEnd())
                    self._reset()
                    return 0
                return 0

            # Need chunk data + trailing CRLF.
            if len(self._buf) < self._chunk_remain + 2:
                return 0

            data_v = self._buf.split_to(self._chunk_remain)
            data = ByteStreamBuffers.to_bytes(data_v)
            self._buf.advance(2)  # CRLF after chunk
            ctx.feed_in(PipelineHttpContentChunk(data))
            self._chunk_remain = None  # next size line

        raise RuntimeError('unreachable')

    def _reset(self) -> None:
        self._head = None
        self._mode = None
        self._remain = 0
        self._chunk_remain = None
        # leave _buf empty; any leftover bytes would imply pipelining, which we currently reject
        if len(self._buf):
            # treat as protocol error
            raise ValueError('unexpected extra bytes after request')
