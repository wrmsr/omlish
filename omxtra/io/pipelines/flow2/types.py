import dataclasses as dc
import typing as ta

from omlish.lite.namespaces import NamespaceClass

from ..core import ChannelPipelineMessages


##


class ChannelPipelineFlowMessages(NamespaceClass):
    @ta.final
    @dc.dataclass(frozen=True)
    class FlushInput(ChannelPipelineMessages.NeverOutbound):  # ~ Netty `ChannelInboundInvoker.fireChannelReadComplete`  # noqa
        pass

    @ta.final
    @dc.dataclass(frozen=True)
    class ReadyForOutput(ChannelPipelineMessages.NeverOutbound):  # ~ Netty `ChannelOutboundInvoker.fireChannelWritabilityChanged`  # noqa
        pass

    @ta.final
    @dc.dataclass(frozen=True)
    class PauseOutput(ChannelPipelineMessages.NeverOutbound):  # ~ Netty `ChannelOutboundInvoker.fireChannelWritabilityChanged`  # noqa
        pass

    #

    @ta.final
    @dc.dataclass(frozen=True)
    class FlushOutput(ChannelPipelineMessages.NeverInbound):  # ~ Netty 'ChannelOutboundInvoker.flush'
        pass

    @ta.final
    @dc.dataclass(frozen=True)
    class ReadyForInput(ChannelPipelineMessages.NeverInbound):  # ~ Netty `ChannelOutboundInvoker.read`
        pass
