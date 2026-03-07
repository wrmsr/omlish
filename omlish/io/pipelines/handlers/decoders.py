# ruff: noqa: UP006
# @omlish-lite
import abc
import typing as ta

from ....lite.abstract import Abstract
from ..core import IoPipelineHandler
from ..core import IoPipelineHandlerContext
from ..core import IoPipelineHandlerFn
from ..core import ShareableIoPipelineHandler
from ..flow.types import IoPipelineFlow
from ..flow.types import IoPipelineFlowMessages


##


class MessageToMessageDecoderIoPipelineHandler(IoPipelineHandler, Abstract):
    @abc.abstractmethod
    def _should_decode(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def _decode(
            self,
            ctx: IoPipelineHandlerContext,
            msg: ta.Any,
            out: ta.List[ta.Any],
    ) -> None:
        raise NotImplementedError

    _called_decode = False
    _produced_messages = False

    def _on_inbound_flush_input(self, ctx: IoPipelineHandlerContext, msg: IoPipelineFlowMessages.FlushInput) -> None:  # noqa
        if not isinstance(self, ShareableIoPipelineHandler):
            if (
                    self._called_decode and
                    not self._produced_messages and
                    not ctx.services[IoPipelineFlow].is_auto_read()
            ):
                ctx.feed_out(IoPipelineFlowMessages.ReadyForInput())

            self._called_decode = False
            self._produced_messages = False

        ctx.feed_in(msg)

    def _on_inbound_should_decode(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        self._called_decode = True

        out: ta.List[ta.Any] = []

        self._decode(ctx, msg, out)

        if not out:
            return

        self._produced_messages = True

        for out_msg in out:
            ctx.feed_in(out_msg)

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineFlowMessages.FlushInput):
            self._on_inbound_flush_input(ctx, msg)

        elif self._should_decode(ctx, msg):
            self._on_inbound_should_decode(ctx, msg)

        else:
            ctx.feed_in(msg)


##


class FnMessageToMessageDecoderIoPipelineHandler(MessageToMessageDecoderIoPipelineHandler):
    def __init__(
            self,
            filter_fn: IoPipelineHandlerFn[ta.Any, bool],  # noqa
            decode_fn: IoPipelineHandlerFn[ta.Any, ta.Iterable[ta.Any]],
    ) -> None:
        super().__init__()

        self._filter_fn = filter_fn
        self._decode_fn = decode_fn

    def _should_decode(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> bool:
        return self._filter_fn(ctx, msg)

    def _decode(
            self,
            ctx: IoPipelineHandlerContext,
            msg: ta.Any,
            out: ta.List[ta.Any],
    ) -> None:
        out.extend(self._decode_fn(ctx, msg))
