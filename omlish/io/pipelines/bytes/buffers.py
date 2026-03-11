# ruff: noqa: UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from ....lite.check import check
from ..core import IoPipelineHandlerContext
from ..core import IoPipelineHandlerNotification
from ..core import IoPipelineHandlerNotifications
from ..flow.types import IoPipelineFlow
from .buffering import OutboundBytesBufferingIoPipelineHandler


##


@ta.final
class OutboundBytesBufferIoPipelineHandler(OutboundBytesBufferingIoPipelineHandler):
    @ta.final
    @dc.dataclass(frozen=True)
    class Config:
        DEFAULT: ta.ClassVar['OutboundBytesBufferIoPipelineHandler.Config']

    Config.DEFAULT = Config()

    def __init__(self, config: ta.Optional[Config] = None) -> None:
        super().__init__()

        if config is None:
            config = self.Config.DEFAULT
        self._config = config

    #

    def outbound_buffered_bytes(self) -> ta.Optional[int]:
        return 0

    #

    def notify(self, ctx: IoPipelineHandlerContext, no: IoPipelineHandlerNotification) -> None:
        if isinstance(no, IoPipelineHandlerNotifications.Added):
            check.not_none(no.ctx.services.find(IoPipelineFlow))

    def outbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        ctx.feed_out(ctx)
