# @omlish-lite
import abc
import dataclasses as dc
import typing as ta

from omlish.lite.abstract import Abstract
from omlish.lite.namespaces import NamespaceClass

from ..core import ChannelPipelineMessages
from ..core import ChannelPipelineService


##


class ChannelPipelineFlowMessages(NamespaceClass):
    @ta.final
    @dc.dataclass(frozen=True)
    class FlushInput(ChannelPipelineMessages.NeverOutbound):  # ~ Netty `ChannelInboundInvoker::fireChannelReadComplete`  # noqa
        pass

    @ta.final
    @dc.dataclass(frozen=True)
    class ReadyForOutput(ChannelPipelineMessages.NeverOutbound):  # ~ Netty `ChannelOutboundInvoker::fireChannelWritabilityChanged`  # noqa
        pass

    @ta.final
    @dc.dataclass(frozen=True)
    class PauseOutput(ChannelPipelineMessages.NeverOutbound):  # ~ Netty `ChannelOutboundInvoker::fireChannelWritabilityChanged`  # noqa
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


##


class ChannelPipelineFlow(ChannelPipelineService, Abstract):
    @property
    @abc.abstractmethod
    def is_auto_read(self) -> bool:
        raise NotImplementedError
