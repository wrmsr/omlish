# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta

from ....logs.base import Logger
from ....logs.levels import NamedLogLevel
from ....logs.modules import get_module_logger
from ..core import ChannelPipelineDirection
from ..core import ChannelPipelineDirectionOrDuplex
from ..core import ChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext


log = get_module_logger(globals())  # noqa


##


class LoggingChannelPipelineHandler(ChannelPipelineHandler):
    def __init__(
            self,
            log: ta.Optional[Logger] = None,  # noqa
            level: ta.Union[int, str] = 'debug',
            *,
            direction: ChannelPipelineDirectionOrDuplex = 'duplex',
    ) -> None:
        super().__init__()

        if log is None:
            log = globals()['log']  # noqa
        self._log = log
        self._level = NamedLogLevel(level)
        self._direction = direction

    def _do_log(
            self,
            ctx: ChannelPipelineHandlerContext,
            direction: ChannelPipelineDirection,
            msg: ta.Any,
    ) -> None:
        self._log.log(
            self._level,
            '%s: %r',
            direction,
            msg,
        )

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if self._direction in ('inbound', 'duplex'):
            self._do_log(ctx, 'inbound', msg)
        ctx.feed_in(msg)

    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if self._direction in ('outbound', 'duplex'):
            self._do_log(ctx, 'outbound', msg)
        ctx.feed_out(msg)
