# @omlish-lite
import abc
import dataclasses as dc
import typing as ta

from omlish.lite.abstract import Abstract
from omlish.lite.namespaces import NamespaceClass

from ..core import ChannelPipelineHandlerContext
from ..core import ChannelPipelineMessages
from ..core import ChannelPipelineService


##


class ChannelPipelineFlowMessages(NamespaceClass):
    """
    Note: these inbound messages will never be sent without a `ChannelPipelineFlow` instance in `channel.services` -
    thus it's safe to refer to `ctx.services[ChannelPipelineFlow]` when handling these.
    """

    #

    @ta.final
    @dc.dataclass(frozen=True)
    class FlushInput(ChannelPipelineMessages.NeverOutbound):  # ~ Netty `ChannelInboundInvoker::fireChannelReadComplete`  # noqa
        pass

    #

    @ta.final
    @dc.dataclass(frozen=True)
    class FlushOutput(ChannelPipelineMessages.NeverInbound):  # ~ Netty 'ChannelOutboundInvoker::flush'
        pass

    @ta.final
    @dc.dataclass(frozen=True)
    class ReadyForInput(ChannelPipelineMessages.NeverInbound):  # ~ Netty `ChannelOutboundInvoker::read`
        pass

    #

    # # TODO:
    # @ta.final
    # @dc.dataclass(frozen=True)
    # class ReadyForOutput(ChannelPipelineMessages.NeverOutbound):  # ~ Netty `ChannelOutboundInvoker::fireChannelWritabilityChanged`  # noqa
    #     pass

    # # TODO:
    # @ta.final
    # @dc.dataclass(frozen=True)
    # class PauseOutput(ChannelPipelineMessages.NeverOutbound):  # ~ Netty `ChannelOutboundInvoker::fireChannelWritabilityChanged`  # noqa
    #     pass


##


class ChannelPipelineFlow(ChannelPipelineService, Abstract):
    @abc.abstractmethod
    def is_auto_read(self) -> bool:
        raise NotImplementedError

    @staticmethod
    def is_auto_read_context(ctx: ChannelPipelineHandlerContext) -> bool:
        return (fc := ctx.services.find(ChannelPipelineFlow)) is None or fc.is_auto_read()
