# ruff: noqa: UP006 UP007 UP043 UP045
# @omlish-lite
"""
TODO:
 - chunked make_chunk_header - https://datatracker.ietf.org/doc/html/rfc9112#name-chunk-extensions
  - and make_content_chunk_data ...
 - fix exception handling lol - do we raise ValueError?? do we return aborted??
 - unify with pipelines.bytes.decoders
"""
import abc
import dataclasses as dc
import typing as ta

from omlish.http.parsing import HttpParser
from omlish.http.parsing import ParsedHttpMessage
from omlish.http.parsing import parse_http_message
from omlish.io.streams.scanning import ScanningByteStreamBuffer
from omlish.io.streams.segmented import SegmentedByteStreamBuffer
from omlish.io.streams.types import BytesLikeOrMemoryview
from omlish.io.streams.types import MutableByteStreamBuffer
from omlish.io.streams.utils import ByteStreamBuffers
from omlish.lite.abstract import Abstract
from omlish.lite.check import check

from ..core import ChannelPipelineMessages


##


@dc.dataclass(frozen=True)
class PipelineHttpDecodingConfig:
    DEFAULT: ta.ClassVar['PipelineHttpDecodingConfig']

    parser_config: ta.Optional[HttpParser.Config] = None

    @dc.dataclass(frozen=True)
    class BufferConfig:
        max_size: ta.Optional[int]
        chunk_size: int

    head_buffer: BufferConfig = BufferConfig(max_size=0x1000, chunk_size=0x1000)

    max_content_chunk_size: ta.Optional[int] = None
    content_chunk_header_buffer: BufferConfig = BufferConfig(max_size=1024, chunk_size=0x10000)

    aggregated_body_buffer: BufferConfig = BufferConfig(max_size=0x10000, chunk_size=0x10000)


PipelineHttpDecodingConfig.DEFAULT = PipelineHttpDecodingConfig()


##


class PipelineHttpDecodingMessageAdapter(Abstract):
    def make_head(self, parsed: ParsedHttpMessage) -> ta.Any:
        raise NotImplementedError

    def make_aborted(self, reason: str) -> ta.Any:
        raise NotImplementedError

    def make_content_chunk_data(self, data: BytesLikeOrMemoryview) -> ta.Any:
        raise NotImplementedError

    def make_end(self) -> ta.Any:
        raise NotImplementedError


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
            adapter: PipelineHttpDecodingMessageAdapter,
            parse_mode: HttpParser.Mode,
            *,
            config: PipelineHttpDecodingConfig = PipelineHttpDecodingConfig.DEFAULT,
    ) -> None:
        super().__init__()

        self._adapter = adapter
        self._parse_mode = parse_mode
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
                self._adapter.make_aborted('EOF before HTTP head complete'),
                msg,
            ]

        if not ByteStreamBuffers.can_bytes(msg):
            return [msg]

        out: ta.List[ta.Any] = []

        for mv in ByteStreamBuffers.iter_segments(msg):
            if self._done:
                out.append(mv)
                continue

            rem_mv: ta.Optional[memoryview] = None

            if (max_buf := self._buf.max_size) is not None:
                rem_buf = max_buf - len(self._buf)

                if len(mv) > rem_buf:
                    self._buf.write(mv[:rem_buf])
                    rem_mv = mv[rem_buf:]
                else:
                    self._buf.write(mv)

            # Look for end of head
            i = self._buf.find(b'\r\n\r\n')
            if i < 0:
                if rem_mv is not None:
                    del self._buf
                    self._done = True

                    return [self._adapter.make_aborted('Head exceeded max buffer size')]

                continue

            # Extract head
            head_view = self._buf.split_to(i + 4)

            # Parse and emit head
            raw = head_view.tobytes()
            parsed = parse_http_message(
                raw,
                mode=self._parse_mode,
                config=self._config.parser_config,
            )

            head = self._adapter.make_head(parsed)
            out.append(head)

            # Forward any remainder bytes (body bytes)
            if len(self._buf):
                rem_view = self._buf.split_to(len(self._buf))
                out.append(rem_view)

            if rem_mv is not None:
                out.append(rem_mv)

            del self._buf
            self._done = True

        return out


##


class PipelineHttpContentChunkDecoder(Abstract):
    def __init__(
            self,
            adapter: PipelineHttpDecodingMessageAdapter,
            *,
            config: PipelineHttpDecodingConfig = PipelineHttpDecodingConfig.DEFAULT,
    ) -> None:
        super().__init__()

        self._adapter = adapter
        self._config = config

    @property
    @abc.abstractmethod
    def done(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def inbound_buffered_bytes(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def inbound(self, msg: ta.Any) -> ta.Sequence[ta.Any]:
        raise NotImplementedError


class UntilFinalInputPipelineHttpContentChunkDecoder(PipelineHttpContentChunkDecoder):
    _done: bool = False

    @property
    def done(self) -> bool:
        return self._done

    def inbound_buffered_bytes(self) -> int:
        return 0

    def inbound(self, msg: ta.Any) -> ta.Sequence[ta.Any]:
        check.state(not self._done)

        if isinstance(msg, ChannelPipelineMessages.FinalInput):
            self._done = True

            return [
                self._adapter.make_end(),
                msg,
            ]

        if not ByteStreamBuffers.can_bytes(msg):
            return [msg]

        out: ta.List[ta.Any] = []

        for mv in ByteStreamBuffers.iter_segments(msg):
            out.append(self._adapter.make_content_chunk_data(mv))

        return out


class ContentLengthPipelineHttpContentChunkDecoder(PipelineHttpContentChunkDecoder):
    def __init__(
            self,
            adapter: PipelineHttpDecodingMessageAdapter,
            content_length: int,
            *,
            config: PipelineHttpDecodingConfig = PipelineHttpDecodingConfig.DEFAULT,
    ) -> None:
        check.arg(content_length > 0)

        super().__init__(
            adapter,
            config=config,
        )

        self._remain = content_length

    @property
    def done(self) -> bool:
        return self._remain < 1

    def inbound_buffered_bytes(self) -> int:
        return 0

    def inbound(self, msg: ta.Any) -> ta.Sequence[ta.Any]:
        check.state(self._remain > 0)

        if isinstance(msg, ChannelPipelineMessages.FinalInput):
            self._remain = 0

            return [
                self._adapter.make_aborted('EOF before HTTP body complete'),
                msg,
            ]

        if not ByteStreamBuffers.can_bytes(msg):
            return [msg]

        out: ta.List[ta.Any] = []

        for mv in ByteStreamBuffers.iter_segments(msg):
            if self._remain < 1:
                out.append(mv)
                continue

            mvl = len(mv)

            if self._remain > mvl:
                out.append(self._adapter.make_content_chunk_data(mv))
                self._remain -= mvl

            elif self._remain == mvl:
                out.append(self._adapter.make_content_chunk_data(mv))
                out.append(self._adapter.make_end())
                self._remain = 0

            else:
                out.append(self._adapter.make_content_chunk_data(mv[:self._remain]))
                out.append(self._adapter.make_end())
                ofs = self._remain
                self._remain = 0
                out.append(mv[ofs:])

        return out


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
            adapter: PipelineHttpDecodingMessageAdapter,
            *,
            config: PipelineHttpDecodingConfig = PipelineHttpDecodingConfig.DEFAULT,
    ) -> None:
        super().__init__(
            adapter,
            config=config,
        )

        self._header_buf = self._new_header_buf()

        self._chunk_remaining = 0
        self._got_cr = False

        self._state: ta.Literal['size', 'data', 'trailer', 'done'] = 'size'

    def _new_header_buf(self) -> MutableByteStreamBuffer:
        return ScanningByteStreamBuffer(SegmentedByteStreamBuffer(
            max_size=self._config.content_chunk_header_buffer.max_size,
            chunk_size=self._config.content_chunk_header_buffer.chunk_size,
        ))

    @property
    def done(self) -> bool:
        return self._state == 'done'

    def inbound_buffered_bytes(self) -> int:
        if self._state == 'done':
            return 0
        return len(self._header_buf)

    def inbound(self, msg: ta.Any) -> ta.Sequence[ta.Any]:
        check.state(self._state != 'done')

        if isinstance(msg, ChannelPipelineMessages.FinalInput):
            del self._header_buf
            self._state = 'done'

            return [
                self._adapter.make_aborted('EOF before chunked encoding complete'),
                msg,
            ]

        if not ByteStreamBuffers.can_bytes(msg):
            return [msg]

        out: ta.List[ta.Any] = []

        for mv in ByteStreamBuffers.iter_segments(msg):
            if not self._process(mv, out):
                break

        return out

    def _process(self, mv: memoryview, out: ta.List[ta.Any]) -> bool:
        if self._state == 'done':
            out.append(mv)
            return True

        elif self._state == 'size':
            return self._process_size(mv, out)

        elif self._state == 'data':
            return self._process_data(mv, out)

        elif self._state == 'trailer':
            return self._process_trailer(mv, out)

        else:
            raise RuntimeError(f'Invalid state: {self._state!r}')

    def _process_size(self, mv: memoryview, out: ta.List[ta.Any]) -> bool:
        rem_mv: ta.Optional[memoryview] = None

        if (max_buf := self._header_buf.max_size) is not None:
            rem_buf = max_buf - len(self._header_buf)

            if len(mv) > rem_buf:
                self._header_buf.write(mv[:rem_buf])
                rem_mv = mv[rem_buf:]
            else:
                self._header_buf.write(mv)

        # Parse chunk size line: <hex-size>\r\n
        i = self._header_buf.find(b'\r\n')
        if i < 0:
            if rem_mv is not None:
                del self._header_buf
                self._state = 'done'

                out.append(self._adapter.make_aborted('Chunk header exceeded max buffer size'))
                return False

            return True  # Need more data

        size_line = self._header_buf.split_to(i + 2)

        size_bytes = size_line.tobytes()[:-2]  # Strip \r\n
        try:
            self._chunk_remaining = int(size_bytes, 16)
        except ValueError as e:
            raise ValueError(f'Invalid chunk size: {size_bytes!r}') from e

        if (mcs := self._config.max_content_chunk_size) is not None and self._chunk_remaining > mcs:
            raise ValueError(f'Content chunk size {self._chunk_remaining} exceeds maximum content chunk size: {mcs}')

        if self._chunk_remaining == 0:
            # Final chunk
            self._state = 'trailer'
        else:
            self._state = 'data'

        if len(self._header_buf) > 0:
            hb = self._header_buf
            self._header_buf = self._new_header_buf()

            for hb_mv in ByteStreamBuffers.iter_segments(hb):
                if not self._process(hb_mv, out):
                    return False

        if rem_mv is not None:
            if not self._process(rem_mv, out):
                return False

        return True

    def _process_data(self, mv: memoryview, out: ta.List[ta.Any]) -> bool:
        mvl = len(mv)
        if mvl < self._chunk_remaining:
            self._chunk_remaining -= mvl
            out.append(self._adapter.make_content_chunk_data(mv))
            return True

        if self._chunk_remaining > 0:
            if mvl == self._chunk_remaining:
                out.append(self._adapter.make_content_chunk_data(mv))
                self._chunk_remaining = 0
                return True

            out.append(self._adapter.make_content_chunk_data(mv[:self._chunk_remaining]))
            mv = mv[self._chunk_remaining:]
            mvl = len(mv)
            self._chunk_remaining = 0

        if mvl < 1:
            return True

        if not self._got_cr:
            if mv[0] != 0x0d:
                raise ValueError(f'Expected \\r\\n after chunk data, got {bytes([mv[0]])!r}')
            self._got_cr = True
            mv = mv[1:]
            mvl -= 1
            if mvl < 1:
                return True

        if mv[0] != 0x0a:
            raise ValueError(f'Expected \\r\\n after chunk data, got {bytes([mv[0]])!r}')
        mv = mv[1:]
        mvl -= 1

        self._got_cr = False
        self._state = 'size'

        if mvl > 0:
            if not self._process(mv, out):
                return False

        return True

    def _process_trailer(self, mv: memoryview, out: ta.List[ta.Any]) -> bool:
        mvl = len(mv)
        if mvl < 1:
            return True

        if not self._got_cr:
            if mv[0] != 0x0d:
                raise ValueError(f'Expected \\r\\n after final chunk, got {bytes([mv[0]])!r}')
            self._got_cr = True
            mv = mv[1:]
            mvl -= 1
            if mvl < 1:
                return True

        if mv[0] != 0x0a:
            raise ValueError(f'Expected \\r\\n after final chunk, got {bytes([mv[0]])!r}')
        mv = mv[1:]
        mvl -= 1

        del self._header_buf
        self._got_cr = False
        self._state = 'done'

        # Emit end marker
        out.append(self._adapter.make_end())

        if mvl > 0:
            out.append(mv)

        return True
