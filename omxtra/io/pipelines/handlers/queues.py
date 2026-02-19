# ruff: noqa: UP006 UP037 UP045
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
from .fns import ChannelPipelineHandlerFn


##


class QueueChannelPipelineHandler(ChannelPipelineHandler, Abstract):
    def __init__(
            self,
            *,
            filter: ta.Optional[ChannelPipelineHandlerFn[ta.Any, bool]] = None,  # noqa
            passthrough: bool = False,
    ) -> None:
        super().__init__()

        self._filter = filter
        self._passthrough = passthrough

        self._q: 'collections.deque[ta.Any]' = collections.deque()

    def __repr__(self) -> str:
        return ''.join([
            f'{type(self).__name__}@{id(self):x}',
            f'<len={len(self._q)}>',
            '(',
            ', '.join([
                *([f'filter={self._filter!r}'] if self._filter is not None else []),
                *([f'passthrough={self._passthrough!r}'] if self._passthrough else []),
            ]),
            ')',
        ])

    #

    def _append(self, msg: ta.Any) -> None:
        self._q.append(msg)

    def _popleft(self) -> ta.Any:
        return self._q.popleft()

    #

    def poll(self) -> ta.Optional[ta.Any]:
        if not self._q:
            return None

        return self._popleft()

    def drain(self) -> ta.List[ta.Any]:
        out: ta.List[ta.Any] = []

        while self._q:
            out.append(self._popleft())

        return out


class InboundQueueChannelPipelineHandler(QueueChannelPipelineHandler):
    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if not (self._filter is not None and not self._filter(ctx, msg)):
            ctx.feed_in(msg)
            return

        self._append(msg)

        if self._passthrough:
            ctx.feed_in(msg)


class OutboundQueueChannelPipelineHandler(QueueChannelPipelineHandler):
    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if not (self._filter is not None and not self._filter(ctx, msg)):
            ctx.feed_out(msg)
            return

        self._append(msg)

        if self._passthrough:
            ctx.feed_out(msg)


class DuplexQueueChannelPipelineHandler(
    InboundQueueChannelPipelineHandler,
    OutboundQueueChannelPipelineHandler,
):
    pass
