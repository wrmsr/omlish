# ruff: noqa: UP006 UP007 UP043 UP045
# @omlish-lite
import abc
import dataclasses as dc
import typing as ta

from omlish.io.streams.errors import FrameTooLargeByteStreamBufferError
from omlish.io.streams.segmented import SegmentedByteStreamBuffer
from omlish.io.streams.types import BytesLike
from omlish.io.streams.types import MutableByteStreamBuffer
from omlish.io.streams.utils import ByteStreamBuffers
from omlish.io.streams.utils import CanByteStreamBuffer
from omlish.lite.abstract import Abstract

from ..bytes.buffering import InboundBytesBufferingChannelPipelineHandler
from ..core import ChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext
from ..core import ChannelPipelineMessages
from ..handlers.decoders import MessageToMessageDecoderChannelPipelineHandler
from .objects import PipelineHttpMessageHead
from .objects import PipelineHttpMessageObjects
from .transferencoding import PipelineHttpTransferEncoding
from .transferencoding import PipelineHttpTransferEncodingError


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
            enabled: bool = True,
    ) -> None:
        super().__init__()

        self._config = config
        self._enabled = enabled

        self._handled_types: ta.Tuple[type, ...] = (
            self._head_type,
            self._content_chunk_data_type,
            self._end_type,
            self._aborted_type,
            self._final_type,
        )

        self._state: PipelineHttpObjectAggregator._State = self._init_state()

    #

    @property
    @abc.abstractmethod
    def _if_content_length_missing(self) -> ta.Literal['none', 'eof']:
        raise NotImplementedError

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

    def _should_handle(self, msg: ta.Any) -> bool:
        return isinstance(msg, self._handled_types)

    def _handle(
            self,
            ctx: ChannelPipelineHandlerContext,
            msg: ta.Any,
            out: ta.List[ta.Any],
    ) -> None:
        if isinstance(msg, self._aborted_type):
            self._state = self._AbortedState(self)
            out.append(msg)
            return

        self._state = self._state.handle(ctx, msg, out)

    #

    def _init_state(self) -> '_State':
        if self._enabled:
            return self._HeadState(self)
        else:
            return self._DisabledHeadState(self)

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
                reason: ta.Union[str, BaseException],
                msg: ta.Optional[ta.Any] = None,
        ) -> 'PipelineHttpObjectAggregator._State':
            nxt_state = self._a._AbortedState(self._a)  # noqa
            out.append(self._a._make_aborted(reason))  # noqa
            if msg is not None:
                out.append(msg)
            return nxt_state

        @abc.abstractmethod
        def handle(
                self,
                ctx: ChannelPipelineHandlerContext,
                msg: ta.Any,
                out: ta.List[ta.Any],
        ) -> 'PipelineHttpObjectAggregator._State':
            raise NotImplementedError

    #

    class _HeadState(_State):
        def handle(
                self,
                ctx: ChannelPipelineHandlerContext,
                msg: ta.Any,
                out: ta.List[ta.Any],
        ) -> 'PipelineHttpObjectAggregator._State':
            if isinstance(msg, self._a._head_type):  # noqa
                try:
                    te = PipelineHttpTransferEncoding.select(
                        msg.headers,
                        if_length_missing=self._a._if_content_length_missing,  # noqa
                    )
                except PipelineHttpTransferEncodingError as e:
                    return self._abort(out, f'Invalid Transfer-Encoding: {e.reason}')

                if te.mode in 'none':
                    return self._a._EndState(self._a, msg, b'')  # noqa

                if (
                        te.length is not None and
                        (max_body := self._a._config.body_buffer.max_size) is not None and  # noqa
                        te.length > max_body
                ):
                    return self._abort(out, FrameTooLargeByteStreamBufferError('aggregation body exceeded max_body'))

                return self._a._BodyState(self._a, msg)  # noqa

            elif isinstance(msg, self._a._final_type):  # noqa
                out.append(msg)
                return self

            else:
                raise TypeError(f'unexpected message type: {type(msg)}')

    #

    class _BodyState(_State):
        def __init__(
                self,
                a: 'PipelineHttpObjectAggregator',
                head: PipelineHttpMessageHead,
        ) -> None:
            super().__init__(a)

            self._head = head

        _buf: ta.Optional[MutableByteStreamBuffer] = None

        @property
        def buf(self) -> ta.Optional[MutableByteStreamBuffer]:
            return self._buf

        def handle(
                self,
                ctx: ChannelPipelineHandlerContext,
                msg: ta.Any,
                out: ta.List[ta.Any],
        ) -> 'PipelineHttpObjectAggregator._State':
            if isinstance(msg, self._a._content_chunk_data_type):  # noqa
                if (buf := self._buf) is None:
                    buf = self._buf = SegmentedByteStreamBuffer(
                        max_size=self._a._config.body_buffer.max_size,  # noqa
                        chunk_size=self._a._config.body_buffer.chunk_size,  # noqa
                    )

                for mv in ByteStreamBuffers.iter_segments(msg.data):
                    buf.write(mv)

                return self

            elif isinstance(msg, self._a._end_type):  # noqa
                body: CanByteStreamBuffer
                if (buf := self._buf) is not None:
                    body = buf.coalesce(len(buf))
                else:
                    body = b''

                full = self._a._make_full(self._head, body)  # noqa
                out.append(full)
                return self._a._init_state()  # noqa

            elif isinstance(msg, self._a._final_type):  # noqa
                return self._abort(out, 'incomplete message body', msg)

            else:
                raise TypeError(f'unexpected message type: {type(msg)}')

    #

    class _EndState(_State):
        def __init__(
                self,
                a: 'PipelineHttpObjectAggregator',
                head: PipelineHttpMessageHead,
                body: BytesLike,
        ) -> None:
            super().__init__(a)

            self._head = head
            self._body = body

        def handle(
                self,
                ctx: ChannelPipelineHandlerContext,
                msg: ta.Any,
                out: ta.List[ta.Any],
        ) -> 'PipelineHttpObjectAggregator._State':
            if isinstance(msg, self._a._end_type):  # noqa
                full = self._a._make_full(self._head, self._body)  # noqa
                out.append(full)
                return self._a._init_state()  # noqa

            elif isinstance(msg, self._a._final_type):  # noqa
                return self._abort(out, 'incomplete message sequence', msg)

            else:
                raise TypeError(f'unexpected message type: {type(msg)}')

    #

    class _DisabledHeadState(_State):
        def handle(
                self,
                ctx: ChannelPipelineHandlerContext,
                msg: ta.Any,
                out: ta.List[ta.Any],
        ) -> 'PipelineHttpObjectAggregator._State':
            out.append(msg)
            if isinstance(msg, self._a._head_type):  # noqa
                return self._a._DisabledEndState(self._a)  # noqa
            return self

    class _DisabledEndState(_State):
        def handle(
                self,
                ctx: ChannelPipelineHandlerContext,
                msg: ta.Any,
                out: ta.List[ta.Any],
        ) -> 'PipelineHttpObjectAggregator._State':
            out.append(msg)
            if isinstance(msg, self._a._end_type):  # noqa
                return self._a._init_state()  # noqa
            return self

    #

    class _AbortedState(_State):
        def handle(
                self,
                ctx: ChannelPipelineHandlerContext,
                msg: ta.Any,
                out: ta.List[ta.Any],
        ) -> 'PipelineHttpObjectAggregator._State':
            if isinstance(msg, ChannelPipelineMessages.MustPropagate):
                out.append(msg)
                return self
            raise NotImplementedError


#


class PipelineHttpObjectAggregatorDecoder(
    InboundBytesBufferingChannelPipelineHandler,
    MessageToMessageDecoderChannelPipelineHandler,
    PipelineHttpObjectAggregator,
    Abstract,
):
    _final_type: ta.Final[type] = ChannelPipelineMessages.FinalInput

    #

    def inbound_buffered_bytes(self) -> int:
        return self.buffered_bytes()

    #

    def _should_decode(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> bool:
        return self._should_handle(msg)

    def _decode(
            self,
            ctx: ChannelPipelineHandlerContext,
            msg: ta.Any,
            out: ta.List[ta.Any],
    ) -> None:
        self._handle(ctx, msg, out)
