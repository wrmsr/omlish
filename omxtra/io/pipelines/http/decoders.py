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
from omlish.lite.check import check

from ..core import ChannelPipelineMessages


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
            on_bytes_consumed: ta.Optional[ta.Callable[[int], None]] = None,
            max_head: int = 0x10000,
            buffer_chunk_size: int = 0x10000,
    ) -> None:
        super().__init__()

        self._parse_mode = parse_mode
        self._make_head = make_head
        self._on_bytes_consumed = on_bytes_consumed

        self._max_head = max_head

        self._buf = ScanningByteStreamBuffer(SegmentedByteStreamBuffer(
            max_bytes=max_head,
            buffer_chunk_size=buffer_chunk_size,
        ))

        self._done = False

    @property
    def done(self) -> bool:
        return self._done

    def inbound(self, msg: ta.Any) -> ta.Generator[ta.Any, None, None]:
        check.state(not self._done)

        if isinstance(msg, ChannelPipelineMessages.Eof):
            # EOF: if we have partial head buffered and haven't parsed head, that's an error.
            raise ValueError('EOF before HTTP head complete')

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

        if (obc := self._on_bytes_consumed) is not None:
            obc(before - after)

        # Parse and emit head
        raw = head_view.tobytes()
        parsed = parse_http_message(raw, mode=self._parse_mode)

        head = self._make_head(parsed)
        yield head

        # Forward any remainder bytes (body bytes)
        if len(self._buf):
            rem = len(self._buf)
            rem_view = self._buf.split_to(rem)
            yield rem_view

        self._done = True


##


class PipelineHttpContentChunkDecoder(Abstract):
    def __init__(
            self,
            make_chunk: ta.Callable[[bytes], ta.Any],
            make_end: ta.Callable[[], ta.Any],
            *,
            on_bytes_consumed: ta.Optional[ta.Callable[[int], None]] = None,
            # buffer_chunk_size: int = 0x10000,
            # _use_scanning_buffer: bool = False,
    ) -> None:
        super().__init__()

        self._make_chunk = make_chunk
        self._make_end = make_end
        self._on_bytes_consumed = on_bytes_consumed

    @property
    @abc.abstractmethod
    def done(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def inbound(self, msg: ta.Any) -> ta.Generator[ta.Any, None, None]:
        raise NotImplementedError


class UntilEofPipelineHttpContentChunkDecoder(PipelineHttpContentChunkDecoder):
    _done: bool = False

    @property
    def done(self) -> bool:
        return self._done

    def inbound(self, msg: ta.Any) -> ta.Generator[ta.Any, None, None]:
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
            if (obc := self._on_bytes_consumed) is not None:
                obc(len(mv))

            yield self._make_chunk(ByteStreamBuffers.memoryview_to_bytes(mv))


class ContentLengthPipelineHttpContentChunkDecoder(PipelineHttpContentChunkDecoder):
    def __init__(
            self,
            make_chunk: ta.Callable[[bytes], ta.Any],
            make_end: ta.Callable[[], ta.Any],
            content_length: int,
            *,
            on_bytes_consumed: ta.Optional[ta.Callable[[int], None]] = None,
    ) -> None:
        check.arg(content_length > 0)

        super().__init__(
            make_chunk,
            make_end,
            on_bytes_consumed=on_bytes_consumed,
        )

        self._remain = content_length

    @property
    def done(self) -> bool:
        return self._remain < 1

    def inbound(self, msg: ta.Any) -> ta.Generator[ta.Any, None, None]:
        check.state(self._remain)

        if isinstance(msg, ChannelPipelineMessages.Eof):
            raise ValueError('EOF before HTTP body complete')

        if not ByteStreamBuffers.can_bytes(msg):
            yield msg
            return

        mvs = list(ByteStreamBuffers.iter_segments(msg))

        i = 0
        while i < len(mvs) and self._remain > 0:
            mv = mvs[i]
            mvl = len(mv)

            if self._remain < mvl:
                yield self._make_chunk(ByteStreamBuffers.memoryview_to_bytes(mv[:self._remain]))

                yield self._make_end()

                # Sets done flag before yielding tail in case it happens to be checked before pulling it out of the
                # generator.
                rem = self._remain
                self._remain = 0

                yield mv[rem:]

                break

            if (obc := self._on_bytes_consumed) is not None:
                obc(mvl)

            yield self._make_chunk(ByteStreamBuffers.memoryview_to_bytes(mv))

            self._remain -= mvl

            i += 1

        while i < len(mvs):
            yield mvs[i]

            i += 1


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
            on_bytes_consumed: ta.Optional[ta.Callable[[int], None]] = None,
            max_chunk_header: int = 1024,
            buffer_chunk_size: int = 0x10000,
    ) -> None:
        super().__init__(
            make_chunk,
            make_end,
            on_bytes_consumed=on_bytes_consumed,
        )

        self._buf = ScanningByteStreamBuffer(SegmentedByteStreamBuffer(
            max_bytes=max_chunk_header,
            buffer_chunk_size=buffer_chunk_size,
        ))

        self._chunk_remaining = 0

        self._state: ta.Literal['size', 'data', 'trailer', 'done'] = 'size'

    @property
    def done(self) -> bool:
        return self._state == 'done'

    def inbound(self, msg: ta.Any) -> ta.Generator[ta.Any, None, None]:
        check.state(self._state != 'done')

        if isinstance(msg, ChannelPipelineMessages.Eof):
            raise ValueError('EOF before HTTP body complete')

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

                if (obc := self._on_bytes_consumed) is not None:
                    obc(before - after)

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

                if (obc := self._on_bytes_consumed) is not None:
                    obc(before - after)

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

                if (obc := self._on_bytes_consumed) is not None:
                    obc(before - after)

                # Emit end marker
                yield self._make_end()

                self._state = 'done'

                for rem in self._buf.segments():
                    yield rem

                return

            elif self._state == 'done':
                raise ValueError('Unexpected data after chunked encoding complete')

            else:
                raise RuntimeError(f'Invalid state: {self._state!r}')
