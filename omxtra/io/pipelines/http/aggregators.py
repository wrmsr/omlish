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
from omlish.io.streams.segmented import SegmentedByteStreamBufferView
from omlish.io.streams.types import BytesLikeOrMemoryview
from omlish.io.streams.types import MutableByteStreamBuffer
from omlish.io.streams.utils import ByteStreamBuffers
from omlish.io.streams.utils import CanByteStreamBuffer
from omlish.lite.abstract import Abstract
from omlish.lite.check import check

from .objects import FullPipelineHttpMessage
from ..bytes.buffering import InboundBytesBufferingChannelPipelineHandler
from ..bytes.decoders import BytesToMessageDecoderChannelPipelineHandler
from ..core import ChannelPipelineHandler
from ..core import ChannelPipelineMessages
from ..core import ChannelPipelineHandlerContext
from .objects import PipelineHttpMessageAborted
from .objects import PipelineHttpMessageEnd
from .objects import PipelineHttpMessageContentChunkData
from .objects import PipelineHttpMessageHead


##


@dc.dataclass(frozen=True)
class PipelineHttpAggregationConfig:
    DEFAULT: ta.ClassVar['PipelineHttpAggregationConfig']

    @dc.dataclass(frozen=True)
    class BufferConfig:
        max_size: ta.Optional[int]
        chunk_size: int

    body_buffer: BufferConfig = BufferConfig(max_size=64 * 1024, chunk_size=64 * 1024)


PipelineHttpAggregationConfig.DEFAULT = PipelineHttpAggregationConfig()


#


class PipelineHttpObjectAggregator(
    ChannelPipelineHandler,
    Abstract,
):
    def __init__(
            self,
            *,
            config: PipelineHttpAggregationConfig = PipelineHttpAggregationConfig.DEFAULT,
    ) -> None:
        super().__init__()

        self._config = config

        self._handled_types: ta.Tuple[type, ...] = (
            self._head_type,
            self._content_chunk_data_type,
            self._end_type,
            self._final_type,
        )

        self._state: PipelineHttpObjectAggregator._State = self._HeadState(self)

    #

    def buffered_bytes(self) -> int:
        if (buf := self._state.buf) is None:
            return 0
        return len(buf)

    #

    @property
    @abc.abstractmethod
    def _head_type(self) -> ta.Type[PipelineHttpMessageHead]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def _content_chunk_data_type(self) -> ta.Type[PipelineHttpMessageContentChunkData]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def _end_type(self) -> ta.Type[PipelineHttpMessageEnd]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def _final_type(self) -> type:
        raise NotImplementedError

    @abc.abstractmethod
    def _make_aborted(self, reason: str) -> PipelineHttpMessageAborted:
        raise NotImplementedError

    @abc.abstractmethod
    def _make_full(
            self,
            head: PipelineHttpMessageHead,
            body: BytesLikeOrMemoryview,
    ) -> FullPipelineHttpMessage:
        raise NotImplementedError

    #

    def _handle(
            self,
            ctx: ChannelPipelineHandlerContext,
            msg: CanByteStreamBuffer,
            feed: ta.Callable[[ta.Any], None],
    ) -> None:
        if not isinstance(msg, self._handled_types):
            feed(msg)
            return

        out: ta.List[ta.Any] = []

        if (ret := self._state.handle(ctx, msg, out)) is not None:
            self._state = ret

        for out_msg in out:
            feed(out_msg)

    #

    class _State(Abstract):
        def __init__(self, a: 'PipelineHttpObjectAggregator') -> None:
            super().__init__()

            self._a = a

        @property
        def buf(self) -> ta.Optional[MutableByteStreamBuffer]:
            return None

        def _abort(
                self,
                out: ta.List[ta.Any],
                reason: str,
                msg: ta.Optional[ta.Any] = None,
        ) -> ta.Optional['PipelineHttpObjectAggregator._State']:
            out.append(self._a._make_aborted(reason))  # noqa
            if msg is not None:
                out.append(msg)
            return self._a._AbortedState(self._a)  # noqa

        @abc.abstractmethod
        def handle(
                self,
                ctx: ChannelPipelineHandlerContext,
                msg: CanByteStreamBuffer,
                out: ta.List[ta.Any],
        ) -> ta.Optional['PipelineHttpObjectAggregator._State']:
            raise NotImplementedError

    #

    class _HeadState(_State):
        def handle(
                self,
                ctx: ChannelPipelineHandlerContext,
                msg: CanByteStreamBuffer,
                out: ta.List[ta.Any],
        ) -> ta.Optional['PipelineHttpObjectAggregator._State']:
            if isinstance(msg, self._a._head_type):
                self._cur_head = msg

                cl = msg.headers.single.get('content-length')
                if cl is None or cl == '':
                    self._want = None

                else:
                    try:
                        self._want = int(cl)
                    except ValueError:
                        raise ValueError('bad Content-Length') from None

                    if self._want < 0:
                        raise ValueError('bad Content-Length')

                    if (max_body := self._buf.max_size) is not None and self._want > max_body:
                        raise FrameTooLargeByteStreamBufferError('request body exceeded max_body')

                if self._want == 0:
                    req = FullPipelineHttpRequest(msg, b'')
                    self._cur_head = None
                    self._want = 0
                    ctx.feed_in(req)

            else:
                out.append(msg)

    #

    class _BodyState(_State):
        def __init__(
                self,
                a: 'PipelineHttpObjectAggregator',
                head: PipelineHttpMessageHead,
                remaining: ta.Optional[int],
        ) -> None:
            super().__init__(a)

            self._head = head
            self._remaining = remaining

        _buf: ta.Optional[MutableByteStreamBuffer] = None

        @property
        def buf(self) -> ta.Optional[MutableByteStreamBuffer]:
            return self._buf

        def handle(
                self,
                ctx: ChannelPipelineHandlerContext,
                msg: CanByteStreamBuffer,
                out: ta.List[ta.Any],
        ) -> ta.Optional['PipelineHttpObjectAggregator._State']:
            # Body bytes
            if self._cur_head is None:
                # Ignore stray bytes (or treat as error). Minimal server: ignore.
                return

            if (buf := self._buf) is None:
                buf = self._buf = ScanningByteStreamBuffer(SegmentedByteStreamBuffer(
                    max_size=self._d._config.head_buffer.max_size,  # noqa
                    chunk_size=self._d._config.head_buffer.chunk_size,  # noqa
                ))

            for mv in ByteStreamBuffers.iter_segments(msg.data):
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

    #

    class _AbortedState(_State):
        def handle(
                self,
                ctx: ChannelPipelineHandlerContext,
                data: CanByteStreamBuffer,
                out: ta.List[ta.Any],
        ) -> ta.Optional['PipelineHttpObjectAggregator._State']:
            raise NotImplementedError
