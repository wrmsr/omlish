# ruff: noqa: UP006 UP045
# @omlish-lite
import abc
import collections
import dataclasses as dc
import typing as ta

from omlish.lite.abstract import Abstract
from omlish.lite.check import check

from .core import ChannelPipelineEvents
from .core import ChannelPipelineFlowControl
from .core import ChannelPipelineHandler
from .core import ChannelPipelineHandlerContext
from .core import PipelineChannel
from .errors import FlowControlValidationChannelPipelineError


##


class ChannelPipelineFlowControlEvents:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    @dc.dataclass(frozen=True)
    class WritabilityChanged:
        is_writable: bool
        pending_outbound: int


class ChannelPipelineFlowCapacityExceededError(Exception):
    pass


##


class ChannelPipelineFlowControlAdapter(Abstract):
    @abc.abstractmethod
    def get_cost(self, msg: ta.Any) -> ta.Optional[int]:
        raise NotImplementedError


##


class FlowControlChannelPipelineHandler(ChannelPipelineFlowControl, ChannelPipelineHandler):
    @dc.dataclass(frozen=True)
    class Config:
        credit: int = 0x100000

        high_watermark: int = 0x100000
        low_watermark: int = 0x80000

        pause_reading_when_unwritable: bool = True

        outbound_capacity: ta.Optional[int] = None
        outbound_overflow_policy: ta.Literal['allow', 'close', 'raise', 'drop'] = 'allow'

        def __post_init__(self) -> None:
            check.arg(self.low_watermark <= self.high_watermark)
            check.arg(self.outbound_capacity is None or self.outbound_capacity >= 0)
            check.in_(self.outbound_overflow_policy, ('allow', 'close', 'raise', 'drop'))

    def __init__(
            self,
            adapter: ChannelPipelineFlowControlAdapter,
            config: Config = Config(),
            *,
            passthrough: bool = False,
            validate: bool = False,
    ) -> None:
        super().__init__()

        self._adapter = adapter
        self._config = config
        self._passthrough = passthrough
        self._validate = validate

        self._inflight = 0
        self._pending_out = 0

        self._out_q: collections.deque[ta.Tuple[ta.Any, int]] = collections.deque()

        self._writable = True

    _channel: PipelineChannel

    #

    @property
    def credit(self) -> int:
        return self._config.credit

    def is_writable(self) -> bool:
        return self._writable

    def pending_outbound(self) -> int:
        return self._pending_out

    #

    def get_cost(self, msg: ta.Any) -> ta.Optional[int]:
        return self._adapter.get_cost(msg)

    def on_consumed(self, handler: ChannelPipelineHandler, cost: int) -> None:
        self._inflight -= cost
        if self._inflight < 0:
            if self._validate:
                raise FlowControlValidationChannelPipelineError(f'inflight count went negative: {self._inflight}')

            self._inflight = 0

    def want_read(self) -> bool:
        if not self._inflight < self._config.credit:
            return False

        if self._config.pause_reading_when_unwritable and not self._writable:
            return False

        return True

    #

    def added(self, ctx: ChannelPipelineHandlerContext) -> None:
        try:
            self._channel  # noqa
        except AttributeError:
            pass
        else:
            raise RuntimeError('ChannelPipelineFlowControlHandler can only be added once')

        self._channel = ctx.channel

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if self._validate and isinstance(msg, ChannelPipelineEvents.Close):
            if self._inflight != 0:
                raise FlowControlValidationChannelPipelineError('inbound Close event with non-zero inflight count')

        if (cost := self._adapter.get_cost(msg)) is None:
            ctx.feed_in(msg)
            return

        self._inflight += cost
        ctx.feed_in(msg)

    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if (cost := self._adapter.get_cost(msg)) is None:
            ctx.feed_out(msg)
            return

        if self._passthrough:
            ctx.feed_out(msg)

        # Overflow policy:
        # - If `outbound_capacity_bytes` is None: never overflow (subject only to writability watermarks).
        # - If set and the enqueue would exceed it:
        #   - 'allow': still enqueue (may grow without bound)
        #   - 'drop': silently drop the new message
        #   - 'close': emit ErrorEvent and close
        #   - 'raise': raise BufferTooLargeByteStreamBufferError (surfaced as ErrorEvent by callers that catch)

        if self._config.outbound_capacity is not None:
            new_total = self._pending_out + cost

            if new_total > self._config.outbound_capacity:
                pol = self._config.outbound_overflow_policy

                if pol == 'allow':
                    pass

                elif pol == 'drop':
                    return

                elif pol == 'close':
                    ctx.emit_out(ChannelPipelineEvents.Error(ChannelPipelineFlowCapacityExceededError()))
                    ctx.channel.feed_close()
                    return

                elif pol == 'raise':
                    raise ChannelPipelineFlowCapacityExceededError

                else:
                    raise ValueError(f'Unknown outbound_overflow_policy: {pol!r}')

        self._out_q.append((msg, cost))
        self._pending_out += cost

        self._update_writability()

    #

    def drain_outbound(self, max_cost: ta.Optional[int] = None) -> ta.List[ta.Any]:
        out: ta.List[ta.Any] = []
        budget = max_cost

        while self._out_q:
            msg, cost = self._out_q[0]

            if budget is not None and out and cost > budget:
                break

            if budget is not None and cost > budget:
                # If the first item exceeds budget, still emit it (caller asked for bytes-ish pacing; splitting items is
                # a higher-level concern).
                pass

            self._out_q.popleft()
            self._pending_out -= cost

            out.append(msg)

            if budget is not None:
                budget -= cost
                if budget <= 0:
                    break

        self._update_writability()
        return out

    def _update_writability(self) -> ta.Optional[bool]:
        before = self._writable
        after = before

        if before and self._pending_out > self._config.high_watermark:
            after = False

        elif (not before) and self._pending_out <= self._config.low_watermark:
            after = True

        if after == before:
            return None

        self._writable = after

        self._channel.feed_in(ChannelPipelineFlowControlEvents.WritabilityChanged(after, self._pending_out))

        return after
