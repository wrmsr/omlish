# ruff: noqa: UP006 UP007 UP043 UP045
# @omlish-lite
import abc
import typing as ta

from omlish.http.parsing import HttpParser
from omlish.http.parsing import ParsedHttpMessage
from omlish.http.parsing import parse_http_message
from omlish.io.streams.scanning import ScanningByteStreamBuffer
from omlish.io.streams.segmented import SegmentedByteStreamBuffer
from omlish.io.streams.segmented import SegmentedByteStreamBufferView
from omlish.io.streams.types import BytesLikeOrMemoryview
from omlish.io.streams.types import MutableByteStreamBuffer
from omlish.io.streams.utils import ByteStreamBuffers
from omlish.io.streams.utils import CanByteStreamBuffer
from omlish.lite.abstract import Abstract

from ...bytes.buffering import InboundBytesBufferingChannelPipelineHandler
from ...bytes.decoders2 import BytesToMessageDecoderChannelPipelineHandler
from ...core import ChannelPipelineHandlerContext
from ..decoders import PipelineHttpDecodingConfig
from ..objects import PipelineHttpMessageAborted
from ..objects import PipelineHttpMessageContentChunkData
from ..objects import PipelineHttpMessageHead


##


class PipelineHttpObjectDecoder(
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

    @abc.abstractmethod
    def _make_head(self, parsed: ParsedHttpMessage) -> PipelineHttpMessageHead:
        raise NotImplementedError

    @abc.abstractmethod
    def _make_aborted(self, reason: str) -> PipelineHttpMessageAborted:
        raise NotImplementedError

    @abc.abstractmethod
    def _make_content_chunk_data(self, data: BytesLikeOrMemoryview) -> PipelineHttpMessageContentChunkData:
        raise NotImplementedError

    @abc.abstractmethod
    def _make_end(self) -> ta.Any:
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

            if next_data is None or len(next_data) == 0:
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
                reason: str,
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
                return (self._d._BodyState(self._d, head), SegmentedByteStreamBufferView(next_mvs))  # Noqa
            else:
                return None

    #

    class _BodyState(_State):
        def __init__(
                self,
                d: 'PipelineHttpObjectDecoder',
                head: PipelineHttpMessageHead,
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
