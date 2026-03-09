# @omlish-lite
import abc
import dataclasses as dc
import typing as ta

from ....lite.abstract import Abstract
from ....lite.namespaces import NamespaceClass
from ..core import IoPipeline
from ..core import IoPipelineHandlerContext
from ..core import IoPipelineMessages


##


class IoPipelineFlowMessages(NamespaceClass):
    """
    Note: these inbound messages will never be sent without a `IoPipelineFlow` instance in `channel.services` -
    thus it's safe to refer to `ctx.services[IoPipelineFlow]` when handling these.
    """

    #

    @ta.final
    @dc.dataclass(frozen=True)
    class FlushInput(  # ~ Netty `ChannelInboundInvoker::fireChannelReadComplete`  # noqa
        IoPipelineMessages.MayPropagate,
        IoPipelineMessages.NeverOutbound,
    ):
        pass

    #

    @ta.final
    @dc.dataclass(frozen=True)
    class FlushOutput(  # ~ Netty 'ChannelOutboundInvoker::flush'
        IoPipelineMessages.MayPropagate,
        IoPipelineMessages.NeverInbound,
    ):
        pass

    @ta.final
    @dc.dataclass(frozen=True)
    class ReadyForInput(  # ~ Netty `ChannelOutboundInvoker::read`
        IoPipelineMessages.MayPropagate,
        IoPipelineMessages.NeverInbound,
    ):
        pass

    #

    # # TODO:
    # @ta.final
    # @dc.dataclass(frozen=True)
    # class ReadyForOutput(  # ~ Netty `ChannelOutboundInvoker::fireChannelWritabilityChanged`  # noqa
    #     IoPipelineMessages.MayPropagate,
    #     IoPipelineMessages.NeverOutbound,
    # ):
    #     pass

    # # TODO:
    # @ta.final
    # @dc.dataclass(frozen=True)
    # class PauseOutput(  # ~ Netty `ChannelOutboundInvoker::fireChannelWritabilityChanged`  # noqa
    #     IoPipelineMessages.MayPropagate,
    #     IoPipelineMessages.NeverOutbound,
    # ):
    #     pass


##


class IoPipelineFlow(Abstract):
    @abc.abstractmethod
    def is_auto_read(
            self: ta.Union[
                'IoPipelineFlow',
                IoPipeline,
                IoPipelineHandlerContext,
                None,
            ],
    ) -> bool:
        # This strange construct grants the ability to do `IoPipelineFlow.is_auto_read(opt_flow)`, which is becoming
        # increasingly frequently useful in real code.
        if self is None:
            return False

        if isinstance(self, IoPipelineFlow):
            return self.is_auto_read()

        if isinstance(self, IoPipelineHandlerContext):
            self = self._pipeline  # noqa

        if isinstance(self, IoPipeline):
            return (fc := self.services.find(IoPipelineFlow)) is None or fc.is_auto_read()

        raise TypeError(self)
