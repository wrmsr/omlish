# ruff: noqa: UP006
# @omlish-lite
import typing as ta

from ..core import ChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext
from ..core import ChannelPipelineHandlerFn
from ..core import ShareableChannelPipelineHandler
from .types import ChannelPipelineFlow
from .types import ChannelPipelineFlowMessages


##


class MessageToMessageDecoder(ChannelPipelineHandler):
    def __init__(self, ty: type, decode: ChannelPipelineHandlerFn[ta.Any, ta.Iterable[ta.Any]]) -> None:
        super().__init__()

        self._ty = ty
        self._decode = decode

    _decode_called = False
    _message_produced = False

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineFlowMessages.FlushInput):
            if not isinstance(self, ShareableChannelPipelineHandler):
                if (
                        self._decode_called and
                        not self._message_produced and
                        not ctx.channel.services[ChannelPipelineFlow].is_auto_read
                ):
                    ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())

                self._decode_called = False
                self._message_produced = False

            ctx.feed_in(msg)
            return

        self._decode_called = True

        out: ta.List[ta.Any] = []
        try:
            if isinstance(msg, self._ty):
                out.extend(self._decode(ctx, msg))
            else:
                out.append(msg)

        finally:
            self._message_produced |= bool(out)
            for out_msg in out:
                ctx.feed_in(out_msg)
