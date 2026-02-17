# ruff: noqa: UP006 UP007 UP043 UP045
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
from omlish.lite.check import check
from omlish.lite.namespaces import NamespaceClass

from ..core import ChannelPipelineHandlerContext
from ..core import ChannelPipelineMessages


##


class PipelineHttpDecoders(NamespaceClass):
    @staticmethod
    def ctx_on_consumed_fn(ctx: ChannelPipelineHandlerContext) -> ta.Optional[ta.Callable[[int], None]]:
        if (bfc := ctx.bytes_flow_control) is None:
            return None

        def inner(n: int) -> None:
            bfc.on_consumed(ctx.handler, n)

        return inner


##


class PipelineHttpHeadDecoder:
    """
    Class for HTTP/1.x head decoders (request or response).

    Handles common logic:
      - Buffering until b'\\r\\n\\r\\n'
      - Parsing request/response line + headers
      - Flow control refund
      - Forwarding remainder bytes
      - EOF handling
    """

    def __init__(
            self,
            parse_mode: HttpParser.Mode,
            make_head: ta.Callable[[ParsedHttpMessage], ta.Any],
            *,
            max_head: int = 0x10000,
            buffer_chunk_size: int = 0x10000,
    ) -> None:
        super().__init__()

        self._parse_mode = parse_mode
        self._make_head = make_head

        self._max_head = max_head

        self._buf = ScanningByteStreamBuffer(SegmentedByteStreamBuffer(
            max_bytes=max_head,
            chunk_size=buffer_chunk_size,
        ))

        self._done = False

    @property
    def done(self) -> bool:
        return self._done

    def inbound(
            self,
            msg: ta.Any,
            *,
            on_bytes_consumed: ta.Optional[ta.Callable[[int], None]] = None,
    ) -> ta.Generator[ta.Any, None, None]:
        check.state(not self._done)

        if isinstance(msg, ChannelPipelineMessages.Eof):
            # EOF: if we have partial head buffered and haven't parsed head, that's an error.
            raise ValueError('EOF before HTTP head complete')  # noqa

        if not ByteStreamBuffers.can_bytes(msg):
            yield msg
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

        if on_bytes_consumed is not None:
            on_bytes_consumed(before - after)

        # Parse and emit head
        raw = head_view.tobytes()
        parsed = parse_http_message(raw, mode=self._parse_mode)

        head = self._make_head(parsed)
        yield head

        # Forward any remainder bytes (body bytes)
        if len(self._buf):
            rem_view = self._buf.split_to(len(self._buf))
            yield rem_view

        self._done = True


##


class PipelineHttpContentChunkDecoder(Abstract):
    def __init__(
            self,
            make_chunk: ta.Callable[[bytes], ta.Any],
            make_end: ta.Callable[[], ta.Any],
    ) -> None:
        super().__init__()

        self._make_chunk = make_chunk
        self._make_end = make_end

    @property
    @abc.abstractmethod
    def done(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def inbound(
            self,
            msg: ta.Any,
            *,
            on_bytes_consumed: ta.Optional[ta.Callable[[int], None]] = None,
    ) -> ta.Generator[ta.Any, None, None]:
        raise NotImplementedError


class UntilEofPipelineHttpContentChunkDecoder(PipelineHttpContentChunkDecoder):
    _done: bool = False

    @property
    def done(self) -> bool:
        return self._done

    def inbound(
            self,
            msg: ta.Any,
            *,
            on_bytes_consumed: ta.Optional[ta.Callable[[int], None]] = None,
    ) -> ta.Generator[ta.Any, None, None]:
        check.state(not self._done)

        if isinstance(msg, ChannelPipelineMessages.Eof):
            yield self._make_end()

            self._done = True

            yield msg
            return

        if not ByteStreamBuffers.can_bytes(msg):
            yield msg
            return

        for mv in ByteStreamBuffers.iter_segments(msg):
            if on_bytes_consumed is not None:
                on_bytes_consumed(len(mv))

            yield self._make_chunk(ByteStreamBuffers.memoryview_to_bytes(mv))


class ContentLengthPipelineHttpContentChunkDecoder(PipelineHttpContentChunkDecoder):
    def __init__(
            self,
            make_chunk: ta.Callable[[bytes], ta.Any],
            make_end: ta.Callable[[], ta.Any],
            content_length: int,
    ) -> None:
        check.arg(content_length > 0)

        super().__init__(
            make_chunk,
            make_end,
        )

        self._remain = content_length

    @property
    def done(self) -> bool:
        return self._remain < 1

    def inbound(
            self,
            msg: ta.Any,
            *,
            on_bytes_consumed: ta.Optional[ta.Callable[[int], None]] = None,
    ) -> ta.Generator[ta.Any, None, None]:
        check.state(self._remain > 0)

        if isinstance(msg, ChannelPipelineMessages.Eof):
            raise ValueError('EOF before HTTP body complete')  # noqa

        if not ByteStreamBuffers.can_bytes(msg):
            yield msg
            return

        for mv in ByteStreamBuffers.iter_segments(msg):
            if self._remain < 1:
                yield mv
                continue

            mvl = len(mv)

            if self._remain > mvl:
                if on_bytes_consumed is not None:
                    on_bytes_consumed(mvl)

                yield self._make_chunk(ByteStreamBuffers.memoryview_to_bytes(mv))
                self._remain -= mvl

            elif self._remain == mvl:
                if on_bytes_consumed is not None:
                    on_bytes_consumed(mvl)

                yield self._make_chunk(ByteStreamBuffers.memoryview_to_bytes(mv))
                yield self._make_end()
                self._remain = 0

            else:
                if on_bytes_consumed is not None:
                    on_bytes_consumed(self._remain)

                yield self._make_chunk(ByteStreamBuffers.memoryview_to_bytes(mv[:self._remain]))
                yield self._make_end()
                ofs = self._remain
                self._remain = 0
                yield mv[ofs:]


class ChunkedPipelineHttpContentChunkDecoder(PipelineHttpContentChunkDecoder):
    """
    Class for HTTP/1.x chunked transfer encoding decoders.

    Handles common logic:
      - Parsing hex chunk sizes
      - Extracting chunk data
      - Validating CRLF delimiters
      - Detecting terminator (0\\r\\n\\r\\n)
      - Flow control refund
      - State machine: 'size' -> 'data' -> 'size' ... -> 'trailer' -> 'done'
    """

    def __init__(
            self,
            make_chunk: ta.Callable[[bytes], ta.Any],
            make_end: ta.Callable[[], ta.Any],
            *,
            max_chunk_header: int = 1024,
            buffer_chunk_size: int = 0x10000,
    ) -> None:
        super().__init__(
            make_chunk,
            make_end,
        )

        self._buf = ScanningByteStreamBuffer(SegmentedByteStreamBuffer(
            max_bytes=max_chunk_header,
            chunk_size=buffer_chunk_size,
        ))

        self._chunk_remaining = 0

        self._state: ta.Literal['size', 'data', 'trailer', 'done'] = 'size'

    @property
    def done(self) -> bool:
        return self._state == 'done'

    def inbound(
            self,
            msg: ta.Any,
            *,
            on_bytes_consumed: ta.Optional[ta.Callable[[int], None]] = None,
    ) -> ta.Generator[ta.Any, None, None]:
        check.state(self._state != 'done')

        if isinstance(msg, ChannelPipelineMessages.Eof):
            raise ValueError('EOF before chunked encoding complete')  # noqa

        if not ByteStreamBuffers.can_bytes(msg):
            yield msg
            return

        # Buffer and decode chunks
        for mv in ByteStreamBuffers.iter_segments(msg):
            if mv:
                self._buf.write(mv)

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

                if on_bytes_consumed is not None:
                    on_bytes_consumed(before - after)

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
                yield self._make_chunk(chunk_data.tobytes())

                if on_bytes_consumed is not None:
                    on_bytes_consumed(before - after)

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

                if on_bytes_consumed is not None:
                    on_bytes_consumed(before - after)

                # Emit end marker
                yield self._make_end()

                self._state = 'done'

                yield from self._buf.segments()

                return

            elif self._state == 'done':
                raise ValueError('Unexpected data after chunked encoding complete')

            else:
                raise RuntimeError(f'Invalid state: {self._state!r}')
