# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import typing as ta

from omlish.http.parsing import HttpParser
from omlish.http.parsing import ParsedHttpMessage
from omlish.http.parsing import parse_http_message
from omlish.io.streams.scanning import ScanningByteStreamBuffer
from omlish.io.streams.segmented import SegmentedByteStreamBuffer
from omlish.io.streams.utils import ByteStreamBuffers
from omlish.lite.abstract import Abstract

from ..core import ChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext
from ..core import ChannelPipelineMessages


##


class PipelineHttpHeadDecoder(ChannelPipelineHandler, Abstract):
    """
    Abstract base class for HTTP/1.x head decoders (request or response).

    Handles common logic:
      - Buffering until b'\\r\\n\\r\\n'
      - Parsing request/response line + headers
      - Flow control refund
      - Forwarding remainder bytes
      - EOF handling

    Subclasses must implement:
      - _parse_mode(): Return HttpParser.Mode.REQUEST or RESPONSE
      - _build_head(): Build PipelineHttpRequestHead or PipelineHttpResponseHead
    """

    def __init__(
            self,
            *,
            max_head: int = 0x10000,
            chunk_size: int = 0x10000,
    ) -> None:
        super().__init__()

        self._max_head = max_head

        self._buf = ScanningByteStreamBuffer(SegmentedByteStreamBuffer(
            max_bytes=max_head,
            chunk_size=chunk_size,
        ))
        self._head_parsed = False

    @abc.abstractmethod
    def _parse_mode(self) -> HttpParser.Mode:
        """Return HttpParser.Mode.REQUEST or HttpParser.Mode.RESPONSE."""

        raise NotImplementedError

    @abc.abstractmethod
    def _build_head(self, parsed: ParsedHttpMessage) -> ta.Any:
        """Build PipelineHttpRequestHead or PipelineHttpResponseHead from parsed message."""

        raise NotImplementedError

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineMessages.Eof):
            # EOF: if we have partial head buffered and haven't parsed head, that's an error.
            if not self._head_parsed and len(self._buf):
                raise ValueError('EOF before HTTP head complete')

            # Reset for next message.
            self._head_parsed = False
            if len(self._buf):
                _ = self._buf.split_to(len(self._buf))

            ctx.feed_in(msg)
            return

        # If we've already parsed the head, passthrough everything.
        if self._head_parsed:
            ctx.feed_in(msg)
            return

        if not ByteStreamBuffers.can_bytes(msg):
            ctx.feed_in(msg)
            return

        # Buffer bytes
        for mv in ByteStreamBuffers.iter_segments(msg):
            if mv:
                self._buf.write(mv)

        # Look for end of head
        i = self._buf.find(b'\r\n\r\n')
        if i < 0:
            return

        # Extract head
        before = len(self._buf)
        head_view = self._buf.split_to(i + 4)
        after = len(self._buf)

        if (bfc := ctx.bytes_flow_control) is not None:
            bfc.on_consumed(self, before - after)

        # Parse and emit head
        raw = head_view.tobytes()
        parsed = parse_http_message(raw, mode=self._parse_mode())
        head = self._build_head(parsed)

        ctx.feed_in(head)
        self._head_parsed = True

        # Forward any remainder bytes (body bytes)
        if len(self._buf):
            rem = len(self._buf)
            rem_view = self._buf.split_to(rem)
            ctx.feed_in(rem_view)


##


PipelineHttpChunkedDecoderState = ta.Literal[  # ta.TypeAlias  # omlish-amalg-typing-no-move
    'size',
    'data',
    'trailer',
    'done',
]


class PipelineHttpChunkedDecoder(ChannelPipelineHandler, Abstract):
    """
    Abstract base class for HTTP/1.x chunked transfer encoding decoders.

    Handles common logic:
      - Parsing hex chunk sizes
      - Extracting chunk data
      - Validating CRLF delimiters
      - Detecting terminator (0\\r\\n\\r\\n)
      - Flow control refund
      - State machine: 'size' -> 'data' -> 'size' ... -> 'trailer' -> 'done'

    Subclasses must implement:
      - _should_enable(): Check if chunked encoding is enabled for this message
      - _emit_end(): Emit PipelineHttpRequestEnd or PipelineHttpResponseEnd
    """

    def __init__(
            self,
            *,
            max_chunk_header: int = 1024,
            chunk_size: int = 0x10000,
    ) -> None:
        super().__init__()

        self._buf = ScanningByteStreamBuffer(SegmentedByteStreamBuffer(
            max_bytes=max_chunk_header,
            chunk_size=chunk_size,
        ))
        self._enabled = False
        self._chunk_remaining = 0
        self._state: PipelineHttpChunkedDecoderState = 'size'

    @abc.abstractmethod
    def _should_enable(self, head: ta.Any) -> bool:
        """Check if Transfer-Encoding includes 'chunked' for this message."""

        raise NotImplementedError

    @abc.abstractmethod
    def _emit_chunk(self, ctx: ChannelPipelineHandlerContext, chunk_data: ta.Any) -> None:
        """Emit PipelineHttpRequestContentChunk or PipelineHttpResponseContentChunk."""

        raise NotImplementedError

    @abc.abstractmethod
    def _emit_end(self, ctx: ChannelPipelineHandlerContext) -> None:
        """Emit PipelineHttpRequestEnd or PipelineHttpResponseEnd."""

        raise NotImplementedError

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineMessages.Eof):
            if self._enabled and self._state != 'done':
                raise ValueError('EOF before chunked encoding complete')
            ctx.feed_in(msg)
            return

        # Check if this is a head message that enables chunked decoding
        if self._is_head_message(msg):
            self._enabled = self._should_enable(msg)
            ctx.feed_in(msg)
            return

        if not self._enabled or not ByteStreamBuffers.can_bytes(msg):
            ctx.feed_in(msg)
            return

        # Buffer and decode chunks
        for mv in ByteStreamBuffers.iter_segments(msg):
            if mv:
                self._buf.write(mv)

        self._decode_chunks(ctx)

    @abc.abstractmethod
    def _is_head_message(self, msg: ta.Any) -> bool:
        """Check if msg is a request/response head."""

        raise NotImplementedError

    def _decode_chunks(self, ctx: ChannelPipelineHandlerContext) -> None:
        """Decode as many complete chunks as possible from buffer."""

        while True:
            if self._state == 'size':
                # Parse chunk size line: <hex-size>\r\n
                i = self._buf.find(b'\r\n')
                if i < 0:
                    return  # Need more data

                before = len(self._buf)
                size_line = self._buf.split_to(i + 2)
                after = len(self._buf)

                size_bytes = size_line.tobytes()[:-2]  # Strip \r\n
                try:
                    self._chunk_remaining = int(size_bytes, 16)
                except ValueError as e:
                    raise ValueError(f'Invalid chunk size: {size_bytes!r}') from e

                if (bfc := ctx.bytes_flow_control) is not None:
                    bfc.on_consumed(self, before - after)

                if self._chunk_remaining == 0:
                    # Final chunk
                    self._state = 'trailer'
                else:
                    self._state = 'data'

            elif self._state == 'data':
                # Read chunk data + trailing \r\n
                needed = self._chunk_remaining + 2
                if len(self._buf) < needed:
                    return  # Need more data

                before = len(self._buf)

                # Extract chunk data
                chunk_data = self._buf.split_to(self._chunk_remaining)

                # Extract trailing \r\n
                trailing = self._buf.split_to(2)
                trailing_bytes = trailing.tobytes()

                after = len(self._buf)

                if trailing_bytes != b'\r\n':
                    raise ValueError(f'Expected \\r\\n after chunk data, got {trailing_bytes!r}')

                # Emit chunk data (wrapped by subclass)
                self._emit_chunk(ctx, chunk_data)

                if (bfc := ctx.bytes_flow_control) is not None:
                    bfc.on_consumed(self, before - after)

                self._chunk_remaining = 0
                self._state = 'size'

            elif self._state == 'trailer':
                # Final \r\n after 0-size chunk
                if len(self._buf) < 2:
                    return  # Need more data

                before = len(self._buf)
                trailing = self._buf.split_to(2)
                after = len(self._buf)

                trailing_bytes = trailing.tobytes()

                if trailing_bytes != b'\r\n':
                    raise ValueError(f'Expected \\r\\n after final chunk, got {trailing_bytes!r}')

                if (bfc := ctx.bytes_flow_control) is not None:
                    bfc.on_consumed(self, before - after)

                # Emit end marker
                self._emit_end(ctx)

                self._state = 'done'
                return

            elif self._state == 'done':
                # Should not receive more data after completion
                if len(self._buf) > 0:
                    raise ValueError('Unexpected data after chunked encoding complete')
                return
