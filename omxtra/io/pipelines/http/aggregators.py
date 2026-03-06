# ruff: noqa: UP006 UP007 UP043 UP045
# @omlish-lite
import abc
import dataclasses as dc
import typing as ta

from omlish.http.parsing import HttpParser
from omlish.http.parsing import ParsedHttpMessage
from omlish.http.parsing import parse_http_message
from omlish.io.streams.errors import FrameTooLargeByteStreamBufferError
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
from .transferencoding import PipelineHttpTransferEncoding
from .transferencoding import PipelineHttpTransferEncodingError
from .objects import PipelineHttpMessageObjects


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
    PipelineHttpMessageObjects,
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

    @property
    @abc.abstractmethod
    def _final_type(self) -> type:
        raise NotImplementedError

    #

    def buffered_bytes(self) -> int:
        if (buf := self._state.buf) is None:
            return 0
        return len(buf)

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

        nxt_state, out = self._state.handle(ctx, msg)

        if nxt_state is not None:
            self._state = nxt_state

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
                reason: ta.Union[str, BaseException],
                msg: ta.Optional[ta.Any] = None,
        ) -> ta.Tuple['PipelineHttpObjectAggregator._State', ta.Sequence[ta.Any]]:
            nxt_state = self._a._abortedstate(self._a)  # noqa
            out: ta.List[ta.Any] = [self._a._make_aborted(reason)]
            if msg is not None:
                out.append(msg)
            return (nxt_state, out)

        @abc.abstractmethod
        def handle(
                self,
                ctx: ChannelPipelineHandlerContext,
                msg: ta.Any,
        ) -> ta.Tuple[ta.Optional['PipelineHttpObjectAggregator._State'], ta.Sequence[ta.Any]]:
            raise NotImplementedError

    #

    class _HeadState(_State):
        def handle(
                self,
                ctx: ChannelPipelineHandlerContext,
                msg: ta.Any,
        ) -> ta.Tuple[ta.Optional['PipelineHttpObjectAggregator._State'], ta.Sequence[ta.Any]]:
            if isinstance(msg, self._a._head_type):
                try:
                    te = PipelineHttpTransferEncoding.select(msg.headers)  # noqa
                except PipelineHttpTransferEncodingError as e:
                    return self._abort(f'Invalid Transfer-Encoding: {e.reason}')

                if te.mode in 'none':
                    return (self._a._EndState(self._a, msg, b''), [])  # noqa

                if (
                        te.length is not None and
                        (max_body := self._a._config.body_buffer.max_size) is not None and
                        te.length > max_body
                ):
                    return self._abort(FrameTooLargeByteStreamBufferError('aggregation body exceeded max_body'))

                return (self._a._BodyState(self._a, msg, te.length), [])  # noqa

            else:
                return (None, [msg])

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
                msg: ta.Any,
        ) -> ta.Tuple[ta.Optional['PipelineHttpObjectAggregator._State'], ta.Sequence[ta.Any]]:
            if isinstance(msg, self._a._content_chunk_data_type):
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

            elif isinstance(msg, self._a._end_type):
                raise NotImplementedError

    #

    class _EndState(_State):
        def __init__(
                self,
                a: 'PipelineHttpObjectAggregator',
                head: PipelineHttpMessageHead,
                body: CanByteStreamBuffer,
        ) -> None:
            super().__init__(a)

            self._head = head
            self._body = body

        def handle(
                self,
                ctx: ChannelPipelineHandlerContext,
                msg: ta.Any,
        ) -> ta.Tuple[ta.Optional['PipelineHttpObjectAggregator._State'], ta.Sequence[ta.Any]]:
            raise NotImplementedError

    #

    class _AbortedState(_State):
        def handle(
                self,
                ctx: ChannelPipelineHandlerContext,
                msg: ta.Any,
        ) -> ta.Tuple[ta.Optional['PipelineHttpObjectAggregator._State'], ta.Sequence[ta.Any]]:
            raise NotImplementedError
