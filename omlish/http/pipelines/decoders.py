# ruff: noqa: UP006 UP007 UP043 UP045
# @omlish-lite
"""
TODO:
 - chunked make_chunk_header - https://datatracker.ietf.org/doc/html/rfc9112#name-chunk-extensions
  - and make_content_chunk_data ...
 - fix exception handling lol - do we raise ValueError?? do we return aborted??
"""
import abc
import dataclasses as dc
import typing as ta

from ...io.pipelines.bytes.buffering import InboundBytesBufferingChannelPipelineHandler
from ...io.pipelines.bytes.decoders import BytesToMessageDecoderChannelPipelineHandler
from ...io.pipelines.core import ChannelPipelineHandlerContext
from ...io.streams.scanning import ScanningByteStreamBuffer
from ...io.streams.segmented import SegmentedByteStreamBuffer
from ...io.streams.segmented import SegmentedByteStreamBufferView
from ...io.streams.types import MutableByteStreamBuffer
from ...io.streams.utils import ByteStreamBuffers
from ...io.streams.utils import CanByteStreamBuffer
from ...lite.abstract import Abstract
from ...lite.check import check
from ..parsing import HttpParser
from ..parsing import parse_http_message
from .objects import PipelineHttpMessageHead
from .objects import PipelineHttpMessageObjects
from .transferencoding import PipelineHttpTransferEncoding
from .transferencoding import PipelineHttpTransferEncodingError


##


@dc.dataclass(frozen=True)
class PipelineHttpDecodingConfig:
    DEFAULT: ta.ClassVar['PipelineHttpDecodingConfig']

    parser_config: ta.Optional[HttpParser.Config] = None

    @dc.dataclass(frozen=True)
    class BufferConfig:
        max_size: ta.Optional[int]
        chunk_size: int

    head_buffer: BufferConfig = BufferConfig(max_size=4 * 1024, chunk_size=4 * 1024)

    max_content_chunk_size: ta.Optional[int] = None
    content_chunk_header_buffer: BufferConfig = BufferConfig(max_size=1024, chunk_size=1024)


PipelineHttpDecodingConfig.DEFAULT = PipelineHttpDecodingConfig()


#


class PipelineHttpObjectDecoder(
    PipelineHttpMessageObjects,
    InboundBytesBufferingChannelPipelineHandler,
    BytesToMessageDecoderChannelPipelineHandler,
    Abstract,
):
    def __init__(
            self,
            *,
            config: PipelineHttpDecodingConfig = PipelineHttpDecodingConfig.DEFAULT,
    ) -> None:
        super().__init__()

        self._config = config

        self._state: PipelineHttpObjectDecoder._State = self._HeadState(self)

    #

    def inbound_buffered_bytes(self) -> int:
        if (buf := self._state.buf) is None:
            return 0
        return len(buf)

    #

    @property
    @abc.abstractmethod
    def _parse_mode(self) -> HttpParser.Mode:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def _if_content_length_missing(self) -> ta.Literal['none', 'eof']:
        raise NotImplementedError

    #

    def _decode(
            self,
            ctx: ChannelPipelineHandlerContext,
            data: CanByteStreamBuffer,
            out: ta.List[ta.Any],
            *,
            final: bool = False,
    ) -> None:
        while True:
            if (ret := self._state.decode(ctx, data, out, final=final)) is None:
                return

            self._state, next_data = ret

            if next_data is None:
                return

            data = next_data

    #

    class _State(Abstract):
        def __init__(self, d: 'PipelineHttpObjectDecoder') -> None:
            super().__init__()

            self._d = d

        @property
        def buf(self) -> ta.Optional[MutableByteStreamBuffer]:
            return None

        def _abort(
                self,
                out: ta.List[ta.Any],
                reason: ta.Union[str, BaseException],
                data: ta.Optional[CanByteStreamBuffer] = None,
        ) -> ta.Optional[ta.Tuple['PipelineHttpObjectDecoder._State', ta.Optional[CanByteStreamBuffer]]]:
            out.append(self._d._make_aborted(reason))  # noqa
            return (self._d._AbortedState(self._d), data)  # noqa

        @abc.abstractmethod
        def decode(
                self,
                ctx: ChannelPipelineHandlerContext,
                data: CanByteStreamBuffer,
                out: ta.List[ta.Any],
                *,
                final: bool = False,
        ) -> ta.Optional[ta.Tuple['PipelineHttpObjectDecoder._State', ta.Optional[CanByteStreamBuffer]]]:
            raise NotImplementedError

    #

    class _HeadState(_State):
        _buf: ta.Optional[MutableByteStreamBuffer] = None

        @property
        def buf(self) -> ta.Optional[MutableByteStreamBuffer]:
            return self._buf

        def decode(
                self,
                ctx: ChannelPipelineHandlerContext,
                data: CanByteStreamBuffer,
                out: ta.List[ta.Any],
                *,
                final: bool = False,
        ) -> ta.Optional[ta.Tuple['PipelineHttpObjectDecoder._State', ta.Optional[CanByteStreamBuffer]]]:
            if final:
                return self._abort(out, 'EOF before HTTP head complete')

            done = False
            next_mvs: ta.List[memoryview]

            for mv in ByteStreamBuffers.iter_segments(data):
                if done:
                    next_mvs.append(mv)  # noqa
                    continue

                if (buf := self._buf) is None:
                    buf = self._buf = ScanningByteStreamBuffer(SegmentedByteStreamBuffer(
                        max_size=self._d._config.head_buffer.max_size,  # noqa
                        chunk_size=self._d._config.head_buffer.chunk_size,  # noqa
                    ))

                rem_mv: ta.Optional[memoryview] = None

                if (max_buf := buf.max_size) is not None:
                    rem_buf = max_buf - len(buf)

                    if len(mv) > rem_buf:
                        buf.write(mv[:rem_buf])
                        rem_mv = mv[rem_buf:]
                    else:
                        buf.write(mv)

                # Look for end of head
                i = buf.find(b'\r\n\r\n')
                if i < 0:
                    if rem_mv is not None:
                        return self._abort(out, 'Head exceeded max buffer size')

                    continue

                # Extract head
                head_view = buf.split_to(i + 4)

                # Parse and emit head
                raw = head_view.tobytes()
                parsed = parse_http_message(
                    raw,
                    mode=self._d._parse_mode,  # noqa
                    config=self._d._config.parser_config,  # noqa
                )

                head = self._d._make_head(parsed)  # noqa
                out.append(head)

                done = True
                next_mvs = []

                # Forward any remainder bytes (body bytes)
                if len(buf):
                    rem_view = buf.split_to(len(buf))
                    next_mvs.extend(rem_view.segments())

                if rem_mv is not None:
                    next_mvs.append(rem_mv)

            if done:
                return (
                    self._d._TransferEncodingState(self._d, head),  # noqa
                    SegmentedByteStreamBufferView.or_else(next_mvs, b''),
                )
            else:
                return None

    #

    class _TransferEncodingState(_State):
        def __init__(self, d: 'PipelineHttpObjectDecoder', head: PipelineHttpMessageHead) -> None:
            super().__init__(d)

            self._head = head

        def decode(
                self,
                ctx: ChannelPipelineHandlerContext,
                data: CanByteStreamBuffer,
                out: ta.List[ta.Any],
                *,
                final: bool = False,
        ) -> ta.Optional[ta.Tuple['PipelineHttpObjectDecoder._State', ta.Optional[CanByteStreamBuffer]]]:
            try:
                te = PipelineHttpTransferEncoding.select(
                    self._head.headers,
                    if_length_missing=self._d._if_content_length_missing,  # noqa
                )
            except PipelineHttpTransferEncodingError as e:
                return self._abort(out, f'Invalid Transfer-Encoding: {e.reason}')

            if te.mode == 'none':
                out.append(self._d._make_end())  # noqa
                return (self._d._DoneState(self._d, self._head), data)  # noqa

            elif te.mode == 'eof':
                return (self._d._UntilEofContentState(self._d, self._head), data)  # noqa

            elif te.mode == 'cl':
                return (self._d._ContentLengthContentState(self._d, self._head, check.not_none(te.length)), data)  # noqa

            elif te.mode == 'chunked':
                return (self._d._HeaderChunkedContentState(self._d, self._head), data)  # noqa

            else:
                raise RuntimeError(f'unexpected mode {te!r}')

    #

    class _ContentState(_State, Abstract):
        def __init__(
                self,
                d: 'PipelineHttpObjectDecoder',
                head: PipelineHttpMessageHead,
        ) -> None:
            super().__init__(d)

            self._head = head

    #

    class _UntilEofContentState(_ContentState):
        def decode(
                self,
                ctx: ChannelPipelineHandlerContext,
                data: CanByteStreamBuffer,
                out: ta.List[ta.Any],
                *,
                final: bool = False,
        ) -> ta.Optional[ta.Tuple['PipelineHttpObjectDecoder._State', ta.Optional[CanByteStreamBuffer]]]:
            for mv in ByteStreamBuffers.iter_segments(data):
                if len(data):
                    out.append(self._d._make_content_chunk_data(mv))  # noqa

            if final:
                out.append(self._d._make_end())  # noqa
                return (self._d._DoneState(self._d, self._head), b'')  # noqa
            else:
                return None

    #

    class _ContentLengthContentState(_ContentState):
        def __init__(
                self,
                d: 'PipelineHttpObjectDecoder',
                head: PipelineHttpMessageHead,
                content_length: int,
        ) -> None:
            check.arg(content_length > 0)

            super().__init__(d, head)

            self._remaining = content_length

        def decode(
                self,
                ctx: ChannelPipelineHandlerContext,
                data: CanByteStreamBuffer,
                out: ta.List[ta.Any],
                *,
                final: bool = False,
        ) -> ta.Optional[ta.Tuple['PipelineHttpObjectDecoder._State', ta.Optional[CanByteStreamBuffer]]]:
            next_mvs: ta.List[memoryview]

            for mv in ByteStreamBuffers.iter_segments(data):
                mvl = len(mv)
                if not mvl:
                    continue

                if self._remaining < 1:
                    next_mvs.append(mv)  # noqa
                    continue

                if self._remaining > mvl:
                    out.append(self._d._make_content_chunk_data(mv))  # noqa
                    self._remaining -= mvl

                elif self._remaining == mvl:
                    out.append(self._d._make_content_chunk_data(mv))  # noqa
                    out.append(self._d._make_end())  # noqa
                    self._remaining = 0
                    next_mvs = []

                else:
                    out.append(self._d._make_content_chunk_data(mv[:self._remaining]))  # noqa
                    out.append(self._d._make_end())  # noqa
                    ofs = self._remaining
                    self._remaining = 0
                    next_mvs = [mv[ofs:]]

            if final and self._remaining > 0:
                return self._abort(out, 'EOF before HTTP body complete')
            elif self._remaining == 0:
                return (
                    self._d._DoneState(self._d, self._head),  # noqa
                    SegmentedByteStreamBufferView.or_else(next_mvs, b''),
                )
            else:
                return None

    #

    class _ChunkedContentState(_ContentState, Abstract):
        pass

    #

    class _HeaderChunkedContentState(_ChunkedContentState):
        _buf: ta.Optional[MutableByteStreamBuffer] = None

        @property
        def buf(self) -> ta.Optional[MutableByteStreamBuffer]:
            return self._buf

        def decode(
                self,
                ctx: ChannelPipelineHandlerContext,
                data: CanByteStreamBuffer,
                out: ta.List[ta.Any],
                *,
                final: bool = False,
        ) -> ta.Optional[ta.Tuple['PipelineHttpObjectDecoder._State', ta.Optional[CanByteStreamBuffer]]]:
            chunk_size: ta.Optional[int] = None
            next_mvs: ta.List[memoryview]

            for mv in ByteStreamBuffers.iter_segments(data):
                if chunk_size is not None:
                    next_mvs.append(mv)  # noqa
                    continue

                if (buf := self._buf) is None:
                    buf = self._buf = ScanningByteStreamBuffer(SegmentedByteStreamBuffer(
                        max_size=self._d._config.content_chunk_header_buffer.max_size,  # noqa
                        chunk_size=self._d._config.content_chunk_header_buffer.chunk_size,  # noqa
                    ))

                rem_mv: ta.Optional[memoryview] = None

                if (max_buf := buf.max_size) is not None:
                    rem_buf = max_buf - len(buf)

                    if len(mv) > rem_buf:
                        buf.write(mv[:rem_buf])
                        rem_mv = mv[rem_buf:]
                    else:
                        buf.write(mv)

                # Parse chunk size line: <hex-size>\r\n
                i = buf.find(b'\r\n')
                if i < 0:
                    if rem_mv is not None:
                        return self._abort(out, 'Chunk header exceeded max buffer size')

                    continue

                size_line = buf.split_to(i + 2)

                size_bytes = size_line.tobytes()[:-2]  # Strip \r\n
                try:
                    chunk_size = int(size_bytes, 16)
                except ValueError:
                    return self._abort(out, f'Invalid chunk size: {size_bytes!r}')

                if (mcs := self._d._config.max_content_chunk_size) is not None and chunk_size > mcs:  # noqa
                    return self._abort(out, f'Content chunk size {chunk_size} exceeds maximum content chunk size: {mcs}')  # noqa

                next_mvs = []

                if len(buf) > 0:
                    next_mvs.extend(buf.segments())

                self._buf = None

                if rem_mv is not None:
                    next_mvs.append(rem_mv)

            if chunk_size is not None:
                if chunk_size == 0:
                    return (
                        self._d._TrailerChunkedContentState(self._d, self._head),  # noqa
                        SegmentedByteStreamBufferView.or_else(next_mvs, b''),
                    )
                else:
                    return (
                        self._d._DataChunkedContentState(self._d, self._head, chunk_size),  # noqa
                        SegmentedByteStreamBufferView.or_else(next_mvs, b''),
                    )
            elif final:
                return self._abort(out, 'EOF before HTTP chunk header complete')
            else:
                return None

    #

    class _DataChunkedContentState(_ChunkedContentState):
        def __init__(
                self,
                d: 'PipelineHttpObjectDecoder',
                head: PipelineHttpMessageHead,
                chunk_size: int,
        ) -> None:
            check.arg(chunk_size > 0)

            super().__init__(d, head)

            self._remaining = chunk_size

        _got_cr = False

        def decode(
                self,
                ctx: ChannelPipelineHandlerContext,
                data: CanByteStreamBuffer,
                out: ta.List[ta.Any],
                *,
                final: bool = False,
        ) -> ta.Optional[ta.Tuple['PipelineHttpObjectDecoder._State', ta.Optional[CanByteStreamBuffer]]]:
            next_mvs: ta.Optional[ta.List[memoryview]] = None

            for mv in ByteStreamBuffers.iter_segments(data):
                if next_mvs is not None:
                    next_mvs.append(mv)
                    continue

                mvl = len(mv)
                if mvl < 1:
                    continue

                if mvl < self._remaining:
                    self._remaining -= mvl
                    out.append(self._d._make_content_chunk_data(mv))  # noqa
                    continue

                if self._remaining > 0:
                    if mvl == self._remaining:
                        out.append(self._d._make_content_chunk_data(mv))  # noqa
                        self._remaining = 0
                        continue

                    out.append(self._d._make_content_chunk_data(mv[:self._remaining]))  # noqa
                    mv = mv[self._remaining:]
                    mvl = len(mv)
                    self._remaining = 0

                if mvl < 1:
                    continue

                if not self._got_cr:
                    if mv[0] != 0x0d:
                        return self._abort(out, f'Expected \\r\\n after chunk data, got {bytes([mv[0]])!r}')
                    self._got_cr = True
                    mv = mv[1:]
                    mvl -= 1
                    if mvl < 1:
                        continue

                if mv[0] != 0x0a:
                    return self._abort(out, f'Expected \\r\\n after chunk data, got {bytes([mv[0]])!r}')
                mv = mv[1:]
                mvl -= 1

                next_mvs = []

                if mvl > 0:
                    next_mvs.append(mv)

            if next_mvs is not None:
                return (
                    self._d._HeaderChunkedContentState(self._d, self._head),  # noqa
                    SegmentedByteStreamBufferView.or_else(next_mvs, b''),
                )
            elif final:
                return self._abort(out, 'EOF before HTTP chunk complete')
            else:
                return None

    #

    class _TrailerChunkedContentState(_ChunkedContentState):
        _got_cr = False

        def decode(
                self,
                ctx: ChannelPipelineHandlerContext,
                data: CanByteStreamBuffer,
                out: ta.List[ta.Any],
                *,
                final: bool = False,
        ) -> ta.Optional[ta.Tuple['PipelineHttpObjectDecoder._State', ta.Optional[CanByteStreamBuffer]]]:
            next_mvs: ta.Optional[ta.List[memoryview]] = None

            for mv in ByteStreamBuffers.iter_segments(data):
                if next_mvs is not None:
                    next_mvs.append(mv)
                    continue

                mvl = len(mv)
                if mvl < 1:
                    continue

                if not self._got_cr:
                    if mv[0] != 0x0d:
                        return self._abort(out, f'Expected \\r\\n after final chunk, got {bytes([mv[0]])!r}')
                    self._got_cr = True
                    mv = mv[1:]
                    mvl -= 1
                    if mvl < 1:
                        continue

                if mv[0] != 0x0a:
                    return self._abort(out, f'Expected \\r\\n after final chunk, got {bytes([mv[0]])!r}')
                mv = mv[1:]
                mvl -= 1

                # Emit end marker
                out.append(self._d._make_end())  # noqa

                next_mvs = []

                if mvl > 0:
                    next_mvs.append(mv)

            if next_mvs is not None:
                return (
                    self._d._DoneState(self._d, self._head),  # noqa
                    SegmentedByteStreamBufferView.of_opt(next_mvs),
                )
            elif final:
                return self._abort(out, 'EOF before HTTP trailer complete')
            else:
                return None

    #

    class _DoneState(_State):
        def __init__(
                self,
                d: 'PipelineHttpObjectDecoder',
                head: ta.Optional[PipelineHttpMessageHead] = None,
        ) -> None:
            super().__init__(d)

            self._head = head

        def decode(
                self,
                ctx: ChannelPipelineHandlerContext,
                data: CanByteStreamBuffer,
                out: ta.List[ta.Any],
                *,
                final: bool = False,
        ) -> ta.Optional[ta.Tuple['PipelineHttpObjectDecoder._State', ta.Optional[CanByteStreamBuffer]]]:
            if not len(data):
                return None

            raise NotImplementedError

    #

    class _AbortedState(_State):
        def decode(
                self,
                ctx: ChannelPipelineHandlerContext,
                data: CanByteStreamBuffer,
                out: ta.List[ta.Any],
                *,
                final: bool = False,
        ) -> ta.Optional[ta.Tuple['PipelineHttpObjectDecoder._State', ta.Optional[CanByteStreamBuffer]]]:
            raise NotImplementedError
