# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta

from ....io.pipelines.core import IoPipelineHandler
from ....io.pipelines.core import IoPipelineHandlerContext
from .objects import WsBinary
from .objects import WsClose
from .objects import WsFrame
from .objects import WsOpcode
from .objects import WsPing
from .objects import WsPong
from .objects import WsText


##


class WebsocketMessageAggregator(IoPipelineHandler):
    """
    Aggregates fragmented data frames into WsText/WsBinary messages. Control frames (PING/PONG/CLOSE) are forwarded as
    WsPing/WsPong/WsClose events.
    """

    _assembling: ta.Optional[ta.Tuple[WsOpcode, bytearray]] = None

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if not isinstance(msg, WsFrame):
            ctx.feed_in(msg)
            return

        op = msg.opcode

        if op == WsOpcode.TEXT or op == WsOpcode.BINARY:
            if msg.fin:
                if op == WsOpcode.TEXT:
                    ctx.feed_in(WsText(msg.payload.decode('utf-8')))
                else:
                    ctx.feed_in(WsBinary(msg.payload))
                return

            self._assembling = (op, bytearray(msg.payload))
            return

        if op == WsOpcode.CONTINUATION:
            if self._assembling is None:
                # Unexpected continuation; drop or raise - here we drop-through as-is if desired but better to surface
                # error upstream; pass-through the raw frame:
                ctx.feed_in(msg)
                return

            first_op, buf = self._assembling
            buf.extend(msg.payload)

            if msg.fin:
                data = bytes(buf)
                self._assembling = None
                if first_op == WsOpcode.TEXT:
                    ctx.feed_in(WsText(data.decode('utf-8')))
                else:
                    ctx.feed_in(WsBinary(data))
            return

        if op == WsOpcode.PING:
            ctx.feed_in(WsPing(msg.payload))
            return

        if op == WsOpcode.PONG:
            ctx.feed_in(WsPong(msg.payload))
            return

        if op == WsOpcode.CLOSE:
            code = 1000
            reason = ''
            if len(msg.payload) >= 2:
                code = int.from_bytes(msg.payload[:2], 'big')
                if len(msg.payload) > 2:
                    try:
                        reason = msg.payload[2:].decode('utf-8')
                    except UnicodeDecodeError:
                        reason = ''
            ctx.feed_in(WsClose(code=code, reason=reason))
            return

        # Unknown/reserved opcodes: pass through
        ctx.feed_in(msg)  # type: ignore[unreachable]
