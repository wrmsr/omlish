# ruff: noqa: UP006 UP007 UP037 UP045
# @omlish-lite
"""
TODO:
 - max size, simple backpressure?
"""
import collections
import typing as ta

from omlish.lite.abstract import Abstract

from ..core import ChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext
from ..core import ChannelPipelineHandlerFn
from ..core import ChannelPipelineMessages


##


class QueueChannelPipelineHandler(ChannelPipelineHandler, Abstract):
    def __init__(
            self,
            *,
            filter: ta.Optional[ChannelPipelineHandlerFn[ta.Any, bool]] = None,  # noqa
            filter_type: ta.Optional[ta.Union[type, ta.Tuple[type, ...]]] = None,
            passthrough: ta.Union[bool, ta.Literal['must_propagate']] = 'must_propagate',
    ) -> None:
        super().__init__()

        self._filter = filter
        self._filter_type = filter_type
        self._passthrough = passthrough

        self._q: collections.deque[ta.Any] = collections.deque()

    def __repr__(self) -> str:
        return ''.join([
            f'{type(self).__name__}@{id(self):x}',
            f'<len={len(self._q)}>',
            '(',
            ', '.join([
                *([f'filter={self._filter!r}'] if self._filter is not None else []),
                *([f'filter_type={self._filter_type!r}'] if self._filter_type is not None else []),
                *([f'passthrough={self._passthrough!r}'] if self._passthrough else []),
            ]),
            ')',
        ])

    #

    def _append(self, msg: ta.Any) -> None:
        self._q.append(msg)

    def _popleft(self) -> ta.Any:
        return self._q.popleft()

    def poll(self) -> ta.Optional[ta.Any]:
        if not self._q:
            return None

        return self._popleft()

    def drain(self) -> ta.List[ta.Any]:
        out: ta.List[ta.Any] = []

        while self._q:
            out.append(self._popleft())

        return out

    #

    def _should_enqueue(self, msg: ta.Any) -> bool:
        if self._filter is not None and not self._filter(msg):
            return False

        if self._filter_type is not None and not isinstance(msg, self._filter_type):
            return False

        return True

    def _should_passthrough(self, msg: ta.Any) -> bool:
        if isinstance(pt := self._passthrough, bool):
            return pt

        elif pt == 'must_propagate':
            return isinstance(msg, ChannelPipelineMessages.MustPropagate)

        else:
            raise RuntimeError(f'Unknown passthrough mode {self._passthrough!r} for {self!r}')

    def _handle(self, msg: ta.Any, feed: ta.Callable[[ta.Any], None]) -> None:
        if not self._should_enqueue(msg):
            feed(msg)
            return

        self._append(msg)

        if self._should_passthrough(msg):
            feed(msg)


class InboundQueueChannelPipelineHandler(QueueChannelPipelineHandler):
    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        self._handle(msg, ctx.feed_in)


class OutboundQueueChannelPipelineHandler(QueueChannelPipelineHandler):
    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        self._handle(msg, ctx.feed_out)


class DuplexQueueChannelPipelineHandler(
    InboundQueueChannelPipelineHandler,
    OutboundQueueChannelPipelineHandler,
):
    pass
