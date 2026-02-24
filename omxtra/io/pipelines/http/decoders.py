# ruff: noqa: UP006 UP007 UP043 UP045
# @omlish-lite
import abc
import dataclasses as dc
import typing as ta

from omlish.http.parsing import HttpParser
from omlish.http.parsing import ParsedHttpMessage
from omlish.http.parsing import parse_http_message
from omlish.io.streams.scanning import ScanningByteStreamBuffer
from omlish.io.streams.segmented import SegmentedByteStreamBuffer
from omlish.io.streams.types import BytesLikeOrMemoryview
from omlish.io.streams.utils import ByteStreamBuffers
from omlish.lite.abstract import Abstract
from omlish.lite.check import check

from ..core import ChannelPipelineMessages


##


@dc.dataclass(frozen=True)
class PipelineHttpDecodingConfig:
    DEFAULT: ta.ClassVar['PipelineHttpDecodingConfig']

    @dc.dataclass(frozen=True)
    class BufferConfig:
        max_size: ta.Optional[int]
        chunk_size: int

    head_buffer: BufferConfig = BufferConfig(max_size=0x1000, chunk_size=0x1000)

    max_content_chunk_size: ta.Optional[int] = None
    # FIXME: should only apply to chunk headers but currently applies to *actual chunk bodies* ...
    content_chunk_header_buffer: BufferConfig = BufferConfig(max_size=1024, chunk_size=0x10000)

    aggregated_body_buffer: BufferConfig = BufferConfig(max_size=0x10000, chunk_size=0x10000)


PipelineHttpDecodingConfig.DEFAULT = PipelineHttpDecodingConfig()


##


class PipelineHttpHeadDecoder:
    """
    Class for HTTP/1.x head decoders (request or response).

    Handles common logic:
      - Buffering until b'\\r\\n\\r\\n'
      - Parsing request/response line + headers
      - Forwarding remainder bytes
      - EOF handling
    """

    def __init__(
            self,
            parse_mode: HttpParser.Mode,
            make_head: ta.Callable[[ParsedHttpMessage], ta.Any],
            make_aborted: ta.Callable[[str], ta.Any],
            *,
            config: PipelineHttpDecodingConfig = PipelineHttpDecodingConfig.DEFAULT,
    ) -> None:
        super().__init__()

        self._parse_mode = parse_mode
        self._make_head = make_head
        self._make_aborted = make_aborted
        self._config = config

        self._buf = ScanningByteStreamBuffer(SegmentedByteStreamBuffer(
            max_size=config.head_buffer.max_size,
            chunk_size=config.head_buffer.chunk_size,
        ))

    _done = False

    @property
    def done(self) -> bool:
        return self._done

    def inbound_buffered_bytes(self) -> int:
        if self._done:
            return 0
        return len(self._buf)

    def inbound(self, msg: ta.Any) -> ta.Sequence[ta.Any]:
        check.state(not self._done)

        if isinstance(msg, ChannelPipelineMessages.FinalInput):
            # EOF: if we have partial head buffered and haven't parsed head, that's an error.

            del self._buf
            self._done = True

            return [
                self._make_aborted('EOF before HTTP head complete'),
                msg,
            ]

        if not ByteStreamBuffers.can_bytes(msg):
            return [msg]

        # Buffer bytes
        # FIXME: lol what dont write everything to buf
        for mv in ByteStreamBuffers.iter_segments(msg):
            if mv:
                self._buf.write(mv)

        # Look for end of head
        i = self._buf.find(b'\r\n\r\n')
        if i < 0:
            return []

        # Extract head
        head_view = self._buf.split_to(i + 4)

        # Parse and emit head
        raw = head_view.tobytes()
        parsed = parse_http_message(raw, mode=self._parse_mode)

        head = self._make_head(parsed)
        out: ta.List[ta.Any] = [head]

        # Forward any remainder bytes (body bytes)
        if len(self._buf):
            rem_view = self._buf.split_to(len(self._buf))
            out.append(rem_view)

        del self._buf
        self._done = True

        return out


##


class PipelineHttpContentChunkDecoder(Abstract):
    def __init__(
            self,
            make_chunk: ta.Callable[[BytesLikeOrMemoryview], ta.Any],
            make_end: ta.Callable[[], ta.Any],
            make_aborted: ta.Callable[[str], ta.Any],
            *,
            config: PipelineHttpDecodingConfig = PipelineHttpDecodingConfig.DEFAULT,
    ) -> None:
        super().__init__()

        self._make_chunk = make_chunk
        self._make_end = make_end
        self._make_aborted = make_aborted
        self._config = config

    @property
    @abc.abstractmethod
    def done(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def inbound_buffered_bytes(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def inbound(self, msg: ta.Any) -> ta.Generator[ta.Any, None, None]:
        raise NotImplementedError


class UntilFinalInputPipelineHttpContentChunkDecoder(PipelineHttpContentChunkDecoder):
    _done: bool = False

    @property
    def done(self) -> bool:
        return self._done

    def inbound_buffered_bytes(self) -> int:
        return 0

    def inbound(self, msg: ta.Any) -> ta.Generator[ta.Any, None, None]:
        check.state(not self._done)

        if isinstance(msg, ChannelPipelineMessages.FinalInput):
            yield self._make_end()

            self._done = True

            yield msg
            return

        if not ByteStreamBuffers.can_bytes(msg):
            yield msg
            return

        for mv in ByteStreamBuffers.iter_segments(msg):
            yield self._make_chunk(mv)


class ContentLengthPipelineHttpContentChunkDecoder(PipelineHttpContentChunkDecoder):
    def __init__(
            self,
            make_chunk: ta.Callable[[BytesLikeOrMemoryview], ta.Any],
            make_end: ta.Callable[[], ta.Any],
            make_aborted: ta.Callable[[str], ta.Any],
            content_length: int,
            *,
            config: PipelineHttpDecodingConfig = PipelineHttpDecodingConfig.DEFAULT,
    ) -> None:
        check.arg(content_length > 0)

        super().__init__(
            make_chunk,
            make_end,
            make_aborted,
            config=config,
        )

        self._remain = content_length

    @property
    def done(self) -> bool:
        return self._remain < 1

    def inbound_buffered_bytes(self) -> int:
        return 0

    def inbound(self, msg: ta.Any) -> ta.Generator[ta.Any, None, None]:
        check.state(self._remain > 0)

        if isinstance(msg, ChannelPipelineMessages.FinalInput):
            yield self._make_aborted('EOF before HTTP body complete')

            self._remain = 0

            yield msg
            return

        if not ByteStreamBuffers.can_bytes(msg):
            yield msg
            return

        for mv in ByteStreamBuffers.iter_segments(msg):
            if self._remain < 1:
                yield mv
                continue

            mvl = len(mv)

            if self._remain > mvl:
                yield self._make_chunk(mv)
                self._remain -= mvl

            elif self._remain == mvl:
                yield self._make_chunk(mv)
                yield self._make_end()
                self._remain = 0

            else:
                yield self._make_chunk(mv[:self._remain])
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
      - State machine: 'size' -> 'data' -> 'size' ... -> 'trailer' -> 'done'
    """

    def __init__(
            self,
            make_chunk: ta.Callable[[BytesLikeOrMemoryview], ta.Any],
            make_end: ta.Callable[[], ta.Any],
            make_aborted: ta.Callable[[str], ta.Any],
            *,
            config: PipelineHttpDecodingConfig = PipelineHttpDecodingConfig.DEFAULT,
    ) -> None:
        super().__init__(
            make_chunk,
            make_end,
            make_aborted,
            config=config,
        )

        self._buf = ScanningByteStreamBuffer(SegmentedByteStreamBuffer(
            max_size=self._config.content_chunk_header_buffer.max_size,
            chunk_size=self._config.content_chunk_header_buffer.chunk_size,
        ))

        self._chunk_remaining = 0

        self._state: ta.Literal['size', 'data', 'trailer', 'done'] = 'size'

    @property
    def done(self) -> bool:
        return self._state == 'done'

    def inbound_buffered_bytes(self) -> int:
        if self._state == 'done':
            return 0
        return len(self._buf)

    def inbound(self, msg: ta.Any) -> ta.Generator[ta.Any, None, None]:
        check.state(self._state != 'done')

        if isinstance(msg, ChannelPipelineMessages.FinalInput):
            yield self._make_aborted('EOF before chunked encoding complete')

            del self._buf
            self._state = 'done'

            yield msg
            return

        if not ByteStreamBuffers.can_bytes(msg):
            yield msg
            return

        # Buffer and decode chunks
        # FIXME: lol no - ignore proper chunk boundaries, direct passthrough
        for mv in ByteStreamBuffers.iter_segments(msg):
            if mv:
                self._buf.write(mv)

        while True:
            if self._state == 'size':
                # Parse chunk size line: <hex-size>\r\n
                i = self._buf.find(b'\r\n')
                if i < 0:
                    return  # Need more data

                size_line = self._buf.split_to(i + 2)

                size_bytes = size_line.tobytes()[:-2]  # Strip \r\n
                try:
                    self._chunk_remaining = int(size_bytes, 16)
                except ValueError as e:
                    raise ValueError(f'Invalid chunk size: {size_bytes!r}') from e

                if (mcs := self._config.max_content_chunk_size) is not None and self._chunk_remaining > mcs:
                    raise ValueError(
                        f'Content chunk size {self._chunk_remaining} exceeds maximum content chunk size: {mcs}',
                    )

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

                # Extract chunk data
                chunk_data = self._buf.split_to(self._chunk_remaining)

                # Extract trailing \r\n
                trailing = self._buf.split_to(2)
                trailing_bytes = trailing.tobytes()

                if trailing_bytes != b'\r\n':
                    raise ValueError(f'Expected \\r\\n after chunk data, got {trailing_bytes!r}')

                # Emit chunk data (wrapped by subclass)
                for mv in chunk_data.segments():
                    yield self._make_chunk(mv)

                self._chunk_remaining = 0
                self._state = 'size'

            elif self._state == 'trailer':
                # Final \r\n after 0-size chunk
                if len(self._buf) < 2:
                    return  # Need more data

                trailing = self._buf.split_to(2)
                trailing_bytes = trailing.tobytes()

                if trailing_bytes != b'\r\n':
                    raise ValueError(f'Expected \\r\\n after final chunk, got {trailing_bytes!r}')

                # Emit end marker
                yield self._make_end()

                if len(self._buf):
                    rem_view = self._buf.split_to(len(self._buf))
                    yield rem_view

                del self._buf
                self._state = 'done'

                return

            elif self._state == 'done':
                raise ValueError('Unexpected data after chunked encoding complete')

            else:
                raise RuntimeError(f'Invalid state: {self._state!r}')
