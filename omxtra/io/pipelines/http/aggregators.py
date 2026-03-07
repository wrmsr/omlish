# ruff: noqa: UP006 UP007 UP043 UP045
# @omlish-lite
import abc
import dataclasses as dc
import typing as ta

from omlish.io.streams.errors import FrameTooLargeByteStreamBufferError
from omlish.io.streams.segmented import SegmentedByteStreamBuffer
from omlish.io.streams.types import MutableByteStreamBuffer
from omlish.io.streams.utils import ByteStreamBuffers
from omlish.io.streams.utils import CanByteStreamBuffer
from omlish.lite.abstract import Abstract

from ..core import ChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext
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

    def _handle(
            self,
            ctx: ChannelPipelineHandlerContext,
            msg: CanByteStreamBuffer,
            feed: ta.Callable[[ta.Any], None],
    ) -> None:
        if not isinstance(msg, self._handled_types):
            feed(msg)
            return

        self._state, out = self._state.handle(ctx, msg)

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
            nxt_state = self._a._AbortedState(self._a)  # noqa
            out: ta.List[ta.Any] = [self._a._make_aborted(reason)]  # noqa
            if msg is not None:
                out.append(msg)
            return (nxt_state, out)

        @abc.abstractmethod
        def handle(
                self,
                ctx: ChannelPipelineHandlerContext,
                msg: ta.Any,
        ) -> ta.Tuple['PipelineHttpObjectAggregator._State', ta.Sequence[ta.Any]]:
            raise NotImplementedError

    #

    class _HeadState(_State):
        def handle(
                self,
                ctx: ChannelPipelineHandlerContext,
                msg: ta.Any,
        ) -> ta.Tuple['PipelineHttpObjectAggregator._State', ta.Sequence[ta.Any]]:
            if isinstance(msg, self._a._head_type):  # noqa
                try:
                    te = PipelineHttpTransferEncoding.select(
                        msg.headers,
                        if_length_missing=self._a._if_content_length_missing,  # noqa
                    )
                except PipelineHttpTransferEncodingError as e:
                    return self._abort(f'Invalid Transfer-Encoding: {e.reason}')

                if te.mode in 'none':
                    return (self._a._EndState(self._a, msg, b''), [])  # noqa

                if (
                        te.length is not None and
                        (max_body := self._a._config.body_buffer.max_size) is not None and  # noqa
                        te.length > max_body
                ):
                    return self._abort(FrameTooLargeByteStreamBufferError('aggregation body exceeded max_body'))

                return (self._a._BodyState(self._a, msg), [])  # noqa

            elif isinstance(msg, self._a._final_type):  # noqa
                return (self, [msg])

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
        ) -> ta.Tuple['PipelineHttpObjectAggregator._State', ta.Sequence[ta.Any]]:
            if isinstance(msg, self._a._content_chunk_data_type):  # noqa
                if (buf := self._buf) is None:
                    buf = self._buf = SegmentedByteStreamBuffer(
                        max_size=self._a._config.body_buffer.max_size,  # noqa
                        chunk_size=self._a._config.body_buffer.chunk_size,  # noqa
                    )

                for mv in ByteStreamBuffers.iter_segments(msg.data):
                    buf.write(mv)

                return (self, [])

            elif isinstance(msg, self._a._end_type):  # noqa
                body: CanByteStreamBuffer
                if (buf := self._buf) is not None:
                    body = buf.coalesce(len(buf))
                else:
                    body = b''

                full = self._a._make_full(self._head, body)  # noqa
                return (self._a._HeadState(self._a), [full])  # noqa

            elif isinstance(msg, self._a._final_type):  # noqa
                return self._abort('incomplete message body', msg)

            else:
                raise TypeError(f'unexpected message type: {type(msg)}')

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
        ) -> ta.Tuple['PipelineHttpObjectAggregator._State', ta.Sequence[ta.Any]]:
            if isinstance(msg, self._a._end_type):  # noqa
                full = self._a._make_full(self._head, self._body)  # noqa
                return (self._a._HeadState(self._a), [full])  # noqa

            elif isinstance(msg, self._a._final_type):  # noqa
                return self._abort('incomplete message sequence', msg)

            else:
                raise TypeError(f'unexpected message type: {type(msg)}')

    #

    class _AbortedState(_State):
        def handle(
                self,
                ctx: ChannelPipelineHandlerContext,
                msg: ta.Any,
        ) -> ta.Tuple['PipelineHttpObjectAggregator._State', ta.Sequence[ta.Any]]:
            raise NotImplementedError
