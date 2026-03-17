# ruff: noqa: UP006 UP007 UP043 UP045
# @omlish-lite
"""
TODO:
 - validating mode?
"""
import abc
import dataclasses as dc
import typing as ta

from ...io.pipelines.bytes.buffering import InboundBytesBufferingIoPipelineHandler
from ...io.pipelines.core import IoPipelineHandler
from ...io.pipelines.core import IoPipelineHandlerContext
from ...io.pipelines.core import IoPipelineMessages
from ...io.pipelines.handlers.decoders import MessageToMessageDecoderIoPipelineHandler
from ...io.streams.errors import FrameTooLargeByteStreamBufferError
from ...io.streams.segmented import SegmentedByteStreamBuffer
from ...io.streams.types import BytesLike
from ...io.streams.types import MutableByteStreamBuffer
from ...io.streams.utils import ByteStreamBuffers
from ...io.streams.utils import CanByteStreamBuffer
from ...lite.abstract import Abstract
from .bodymodes import IoPipelineHttpBodyMode
from .bodymodes import IoPipelineHttpBodyModeError
from .objects import IoPipelineHttpMessageHead
from .objects import IoPipelineHttpMessageObjects


##


@dc.dataclass(frozen=True)
class IoPipelineHttpAggregationConfig:
    DEFAULT: ta.ClassVar['IoPipelineHttpAggregationConfig']

    @dc.dataclass(frozen=True)
    class BufferConfig:
        max_size: ta.Optional[int]
        chunk_size: int

    body_buffer: BufferConfig = BufferConfig(max_size=64 * 1024, chunk_size=64 * 1024)


IoPipelineHttpAggregationConfig.DEFAULT = IoPipelineHttpAggregationConfig()


#


class IoIoPipelineHttpObjectAggregator(
    IoPipelineHttpMessageObjects,
    IoPipelineHandler,
    Abstract,
):
    def __init__(
            self,
            *,
            config: IoPipelineHttpAggregationConfig = IoPipelineHttpAggregationConfig.DEFAULT,
            enabled: ta.Union[bool, ta.Literal['unless_chunked']] = True,
    ) -> None:
        super().__init__()

        self._config = config
        self._enabled = enabled

        self._handled_types: ta.Tuple[type, ...] = (
            self._head_type,
            self._chunk_type,
            self._end_chunk_type,
            self._last_chunk_type,
            self._chunked_trailers_type,
            self._body_data_type,
            self._end_type,
            self._aborted_type,
            self._final_type,
        )

        self._state: IoIoPipelineHttpObjectAggregator._State = self._init_state()

    @property
    def enabled(self) -> ta.Union[bool, ta.Literal['unless_chunked']]:
        return self._enabled

    def set_enabled(self, enabled: ta.Union[bool, ta.Literal['unless_chunked']]) -> None:
        self._enabled = enabled

    #

    @property
    @abc.abstractmethod
    def _if_content_length_missing(self) -> ta.Literal['empty', 'eof']:
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
            ctx: IoPipelineHandlerContext,
            msg: ta.Any,
            out: ta.List[ta.Any],
    ) -> None:
        if isinstance(msg, self._aborted_type):
            self._state = self._AbortedState(self)
            out.append(msg)
            return

        while True:
            if (ret := self._state.handle(ctx, msg, out)) is None:
                return

            self._state, next_msg = ret

            if next_msg is None:
                return

            msg = next_msg

    #

    def _init_state(self) -> '_State':
        if self._enabled is True:
            return self._HeadState(self)
        elif self._enabled == 'unless_chunked':
            return self._UnlessChunkedHeadState(self)
        else:
            return self._DisabledHeadState(self)

    #

    class _State(Abstract):
        def __init__(self, a: 'IoIoPipelineHttpObjectAggregator') -> None:
            super().__init__()

            self._a = a

        @property
        def buf(self) -> ta.Optional[MutableByteStreamBuffer]:
            return None

        def _abort(
                self,
                out: ta.List[ta.Any],
                reason: ta.Union[str, BaseException],
                out_msg: ta.Optional[ta.Any] = None,
        ) -> ta.Optional[ta.Tuple['IoIoPipelineHttpObjectAggregator._State', ta.Optional[ta.Any]]]:
            nxt_state = self._a._AbortedState(self._a)  # noqa
            out.append(self._a._make_aborted(reason))  # noqa
            if out_msg is not None:
                out.append(out_msg)
            return (nxt_state, None)

        @abc.abstractmethod
        def handle(
                self,
                ctx: IoPipelineHandlerContext,
                msg: ta.Any,
                out: ta.List[ta.Any],
        ) -> ta.Optional[ta.Tuple['IoIoPipelineHttpObjectAggregator._State', ta.Optional[ta.Any]]]:
            raise NotImplementedError

    #

    class _HeadState(_State):
        def handle(
                self,
                ctx: IoPipelineHandlerContext,
                msg: ta.Any,
                out: ta.List[ta.Any],
        ) -> ta.Optional[ta.Tuple['IoIoPipelineHttpObjectAggregator._State', ta.Optional[ta.Any]]]:
            if isinstance(msg, self._a._head_type):  # noqa
                try:
                    te = IoPipelineHttpBodyMode.select(
                        msg.headers,
                        if_length_missing=self._a._if_content_length_missing,  # noqa
                    )
                except IoPipelineHttpBodyModeError as e:
                    return self._abort(out, f'Invalid Transfer-Encoding: {e.reason}')

                if te.mode == 'empty':
                    return (self._a._EndState(self._a, msg, b''), None)  # noqa

                if (
                        te.length is not None and
                        (max_body := self._a._config.body_buffer.max_size) is not None and  # noqa
                        te.length > max_body
                ):
                    return self._abort(out, FrameTooLargeByteStreamBufferError('aggregation body exceeded max_body'))

                return (self._a._BodyState(self._a, msg), None)  # noqa

            elif isinstance(msg, self._a._final_type):  # noqa
                out.append(msg)
                return None

            else:
                raise TypeError(f'unexpected message type: {type(msg)}')

    #

    class _BodyState(_State):
        def __init__(
                self,
                a: 'IoIoPipelineHttpObjectAggregator',
                head: IoPipelineHttpMessageHead,
        ) -> None:
            super().__init__(a)

            self._head = head

        _buf: ta.Optional[MutableByteStreamBuffer] = None

        @property
        def buf(self) -> ta.Optional[MutableByteStreamBuffer]:
            return self._buf

        def handle(
                self,
                ctx: IoPipelineHandlerContext,
                msg: ta.Any,
                out: ta.List[ta.Any],
        ) -> ta.Optional[ta.Tuple['IoIoPipelineHttpObjectAggregator._State', ta.Optional[ta.Any]]]:
            if isinstance(msg, self._a._body_data_type):  # noqa
                if (buf := self._buf) is None:
                    buf = self._buf = SegmentedByteStreamBuffer(
                        max_size=self._a._config.body_buffer.max_size,  # noqa
                        chunk_size=self._a._config.body_buffer.chunk_size,  # noqa
                    )

                for mv in ByteStreamBuffers.iter_segments(msg.data):
                    buf.write(mv)

                return None

            elif isinstance(msg, (
                    self._a._chunk_type,  # noqa
                    self._a._end_chunk_type,  # noqa
                    self._a._last_chunk_type,  # noqa
                    self._a._chunked_trailers_type,  # noqa
            )):
                return None

            elif isinstance(msg, self._a._end_type):  # noqa
                body: CanByteStreamBuffer
                if (buf := self._buf) is not None:
                    body = buf.coalesce(len(buf))
                else:
                    body = b''

                full = self._a._make_full(self._head, body)  # noqa
                out.append(full)
                return (self._a._init_state(), None)  # noqa

            elif isinstance(msg, self._a._final_type):  # noqa
                return self._abort(out, 'incomplete message body', msg)

            else:
                raise TypeError(f'unexpected message type: {type(msg)}')

    #

    class _EndState(_State):
        def __init__(
                self,
                a: 'IoIoPipelineHttpObjectAggregator',
                head: IoPipelineHttpMessageHead,
                body: BytesLike,
        ) -> None:
            super().__init__(a)

            self._head = head
            self._body = body

        def handle(
                self,
                ctx: IoPipelineHandlerContext,
                msg: ta.Any,
                out: ta.List[ta.Any],
        ) -> ta.Optional[ta.Tuple['IoIoPipelineHttpObjectAggregator._State', ta.Optional[ta.Any]]]:
            if isinstance(msg, self._a._end_type):  # noqa
                full = self._a._make_full(self._head, self._body)  # noqa
                out.append(full)
                return (self._a._init_state(), None)  # noqa

            elif isinstance(msg, self._a._final_type):  # noqa
                return self._abort(out, 'incomplete message sequence', msg)

            else:
                raise TypeError(f'unexpected message type: {type(msg)}')

    #

    class _UnlessChunkedHeadState(_State):
        def handle(
                self,
                ctx: IoPipelineHandlerContext,
                msg: ta.Any,
                out: ta.List[ta.Any],
        ) -> ta.Optional[ta.Tuple['IoIoPipelineHttpObjectAggregator._State', ta.Optional[ta.Any]]]:
            if isinstance(msg, self._a._head_type):  # noqa
                try:
                    te = IoPipelineHttpBodyMode.select(
                        msg.headers,
                        if_length_missing=self._a._if_content_length_missing,  # noqa
                    )
                except IoPipelineHttpBodyModeError as e:
                    return self._abort(out, f'Invalid Transfer-Encoding: {e.reason}')

                if te.mode != 'chunked':
                    return (self._a._HeadState(self._a), msg)  # noqa
                else:
                    out.append(msg)
                    return (self._a._ReInitEndState(self._a), None)  # noqa

            out.append(msg)
            return None

    class _DisabledHeadState(_State):
        def handle(
                self,
                ctx: IoPipelineHandlerContext,
                msg: ta.Any,
                out: ta.List[ta.Any],
        ) -> ta.Optional[ta.Tuple['IoIoPipelineHttpObjectAggregator._State', ta.Optional[ta.Any]]]:
            out.append(msg)

            if isinstance(msg, self._a._head_type):  # noqa
                return (self._a._ReInitEndState(self._a), None)  # noqa

            return None

    class _ReInitEndState(_State):
        def handle(
                self,
                ctx: IoPipelineHandlerContext,
                msg: ta.Any,
                out: ta.List[ta.Any],
        ) -> ta.Optional[ta.Tuple['IoIoPipelineHttpObjectAggregator._State', ta.Optional[ta.Any]]]:
            out.append(msg)

            if isinstance(msg, self._a._end_type):  # noqa
                return (self._a._init_state(), None)  # noqa

            return None

    #

    class _AbortedState(_State):
        def handle(
                self,
                ctx: IoPipelineHandlerContext,
                msg: ta.Any,
                out: ta.List[ta.Any],
        ) -> ta.Optional[ta.Tuple['IoIoPipelineHttpObjectAggregator._State', ta.Optional[ta.Any]]]:
            if isinstance(msg, IoPipelineMessages.MustPropagate):
                out.append(msg)
                return None

            raise NotImplementedError


#


class IoPipelineHttpObjectAggregatorDecoder(
    InboundBytesBufferingIoPipelineHandler,
    MessageToMessageDecoderIoPipelineHandler,
    IoIoPipelineHttpObjectAggregator,
    Abstract,
):
    _final_type: ta.Final[type] = IoPipelineMessages.FinalInput

    #

    def inbound_buffered_bytes(self) -> int:
        return self.buffered_bytes()

    #

    def _should_decode(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> bool:
        return self._should_handle(msg)

    def _decode(
            self,
            ctx: IoPipelineHandlerContext,
            msg: ta.Any,
            out: ta.List[ta.Any],
    ) -> None:
        self._handle(ctx, msg, out)
