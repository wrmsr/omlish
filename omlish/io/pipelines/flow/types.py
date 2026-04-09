# ruff: noqa: UP007
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
    def _get_instance(
            self: ta.Union[
                'IoPipelineFlow',
                IoPipeline,
                IoPipelineHandlerContext,
                None,
            ],
    ) -> ta.Optional['IoPipelineFlow']:
        # This strange construct grants the ability to do things like `IoPipelineFlow.is_auto_read(opt_flow)`, which are
        # becoming increasingly frequently useful in real code.
        if self is None:
            return None

        if isinstance(self, IoPipelineFlow):
            return self

        if isinstance(self, IoPipelineHandlerContext):
            self = self._pipeline  # noqa

        if isinstance(self, IoPipeline):
            return self.services.find(IoPipelineFlow)

        raise TypeError(self)

    #

    @abc.abstractmethod
    def is_auto_read(
            self: ta.Union[
                'IoPipelineFlow',
                IoPipeline,
                IoPipelineHandlerContext,
                None,
            ],
    ) -> bool:
        return (fc := IoPipelineFlow._get_instance(self)) is None or fc.is_auto_read()

    #

    @ta.final
    @classmethod
    def maybe_flush_output(cls, ctx: IoPipelineHandlerContext) -> None:
        if cls._get_instance(ctx) is not None:
            ctx.feed_out(IoPipelineFlowMessages.FlushOutput())

    @ta.final
    @classmethod
    def maybe_ready_for_input(cls, ctx: IoPipelineHandlerContext) -> None:
        if (fc := cls._get_instance(ctx)) is not None and not fc.is_auto_read():
            ctx.feed_out(IoPipelineFlowMessages.ReadyForInput())
