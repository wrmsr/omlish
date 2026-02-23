# ruff: noqa: UP006
# @omlish-lite
import abc
import typing as ta

from omlish.lite.abstract import Abstract

from ..core import ChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext
from ..core import ChannelPipelineHandlerFn
from ..core import ShareableChannelPipelineHandler
from ..errors import DecodingChannelPipelineError
from ..flow.types import ChannelPipelineFlow
from ..flow.types import ChannelPipelineFlowMessages


##


class MessageToMessageDecoderChannelPipelineHandler(ChannelPipelineHandler, Abstract):
    @abc.abstractmethod
    def _should_decode(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def _decode(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
        raise NotImplementedError

    _called_decode = False
    _produced_messages = False

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineFlowMessages.FlushInput):
            if not isinstance(self, ShareableChannelPipelineHandler):
                if (
                        self._called_decode and
                        not self._produced_messages and
                        not ctx.services[ChannelPipelineFlow].is_auto_read()
                ):
                    ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())

                self._called_decode = False
                self._produced_messages = False

            ctx.feed_in(msg)
            return

        if not self._should_decode(ctx, msg):
            ctx.feed_in(msg)
            return

        self._called_decode = True

        try:
            out = list(self._decode(ctx, msg))

        except DecodingChannelPipelineError:
            raise
        except Exception as e:
            raise DecodingChannelPipelineError from e

        if not out:
            return

        self._produced_messages = True

        for out_msg in out:
            ctx.feed_in(out_msg)


##


class FnMessageToMessageDecoderChannelPipelineHandler(MessageToMessageDecoderChannelPipelineHandler):
    def __init__(
            self,
            filter_fn: ChannelPipelineHandlerFn[ta.Any, bool],  # noqa
            decode_fn: ChannelPipelineHandlerFn[ta.Any, ta.Iterable[ta.Any]],
    ) -> None:
        super().__init__()

        self._filter_fn = filter_fn
        self._decode_fn = decode_fn

    def _should_decode(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> bool:
        return self._filter_fn(ctx, msg)

    def _decode(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
        return self._decode_fn(ctx, msg)
