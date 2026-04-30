# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import os
import typing as ta

from ....io.pipelines.core import IoPipelineHandler
from ....io.pipelines.core import IoPipelineHandlerContext
from ....lite.namespaces import NamespaceClass
from .objects import WsBinary
from .objects import WsClose
from .objects import WsFrame
from .objects import WsOpcode
from .objects import WsPing
from .objects import WsPong
from .objects import WsText


##


class WebsocketFrames(NamespaceClass):
    @staticmethod
    def mask_xor(data: bytes, key: bytes) -> bytes:
        out = bytearray(len(data))
        k0, k1, k2, k3 = key
        for i, b in enumerate(data):
            j = i & 3
            kb = k0 if j == 0 else k1 if j == 1 else k2 if j == 2 else k3
            out[i] = b ^ kb
        return bytes(out)


class WebsocketFrameEncoder(IoPipelineHandler):
    """
    Encodes WsFrame or high-level WsText/WsBinary/WsPing/WsPong/WsClose into bytes. If is_client=True, applies masking
    as required by RFC 6455.
    """

    def __init__(self, *, mask: bool = False) -> None:
        super().__init__()

        self._mask = mask

    def outbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, WsFrame):
            ctx.feed_out(self._encode_frame(msg, mask=self._mask))
            return

        if isinstance(msg, WsText):
            frame = WsFrame(fin=True, opcode=WsOpcode.TEXT, payload=msg.text.encode('utf-8'))
            ctx.feed_out(self._encode_frame(frame, mask=self._mask))
            return

        if isinstance(msg, WsBinary):
            frame = WsFrame(fin=True, opcode=WsOpcode.BINARY, payload=msg.data)
            ctx.feed_out(self._encode_frame(frame, mask=self._mask))
            return

        if isinstance(msg, WsPing):
            frame = WsFrame(fin=True, opcode=WsOpcode.PING, payload=msg.data)
            ctx.feed_out(self._encode_frame(frame, mask=self._mask))
            return

        if isinstance(msg, WsPong):
            frame = WsFrame(fin=True, opcode=WsOpcode.PONG, payload=msg.data)
            ctx.feed_out(self._encode_frame(frame, mask=self._mask))
            return

        if isinstance(msg, WsClose):
            payload = b''
            if msg.code or msg.reason:
                payload = msg.code.to_bytes(2, 'big')
                if msg.reason:
                    payload += msg.reason.encode('utf-8')
            frame = WsFrame(fin=True, opcode=WsOpcode.CLOSE, payload=payload)
            ctx.feed_out(self._encode_frame(frame, mask=self._mask))
            return

        ctx.feed_out(msg)

    def _encode_frame(self, frame: WsFrame, *, mask: bool) -> bytes:
        b0 = (
            (0x80 if frame.fin else 0x00) |
            (0x40 if frame.rsv1 else 0) |
            (0x20 if frame.rsv2 else 0) |
            (0x10 if frame.rsv3 else 0) |
            (int(frame.opcode) & 0x0F)
        )
        payload = frame.payload
        ln = len(payload)

        h = bytearray()
        h.append(b0)

        mask_bit = 0x80 if mask else 0x00

        if ln < 126:
            h.append(mask_bit | ln)
        elif ln < (1 << 16):
            h.append(mask_bit | 126)
            h.extend(ln.to_bytes(2, 'big'))
        else:
            h.append(mask_bit | 127)
            h.extend(ln.to_bytes(8, 'big'))

        if mask:
            key = os.urandom(4)
            h.extend(key)
            payload = WebsocketFrames.mask_xor(payload, key)

        return bytes(h) + payload


class WebsocketFrameDecoder(IoPipelineHandler):
    """
    Decodes inbound bytes into WsFrame objects. If expect_masked is True/False, validates the MASK bit accordingly; if
    None, accepts either.
    """

    def __init__(self, *, expect_masked: bool) -> None:
        super().__init__()

        self._expect_mask = expect_masked

        self._buf = bytearray()

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, (bytes, bytearray, memoryview)):
            self._buf.extend(bytes(msg))
            self._drain(ctx)
            return

        ctx.feed_in(msg)

    def _drain(self, ctx: IoPipelineHandlerContext) -> None:
        while True:
            frm = self._try_parse_one()
            if frm is None:
                break
            ctx.feed_in(frm)

    def _try_parse_one(self) -> ta.Optional[WsFrame]:
        b = self._buf
        if len(b) < 2:
            return None

        b0 = b[0]
        b1 = b[1]

        fin = bool(b0 & 0x80)
        rsv1 = bool(b0 & 0x40)
        rsv2 = bool(b0 & 0x20)
        rsv3 = bool(b0 & 0x10)
        opcode = WsOpcode(b0 & 0x0F)

        masked = bool(b1 & 0x80)
        ln = (b1 & 0x7F)
        o = 2

        if ln == 126:
            if len(b) < o + 2:
                return None
            ln = int.from_bytes(b[o:o + 2], 'big')
            o += 2
        elif ln == 127:
            if len(b) < o + 8:
                return None
            ln = int.from_bytes(b[o:o + 8], 'big')
            o += 8

        key = None
        if masked:
            if len(b) < o + 4:
                return None
            key = bytes(b[o:o + 4])
            o += 4

        if len(b) < o + ln:
            return None

        payload = bytes(b[o:o + ln])
        del b[:o + ln]

        if self._expect_mask is True and not masked:
            raise ValueError('expected masked websocket frame')
        if self._expect_mask is False and masked:
            # We'll unmask but still consider it an error in strict mode; for now accept and unmask.
            pass

        if masked and key is not None:
            payload = WebsocketFrames.mask_xor(payload, key)

        # Basic control-frame checks
        if opcode in (WsOpcode.CLOSE, WsOpcode.PING, WsOpcode.PONG):
            if not fin or ln > 125:
                raise ValueError('invalid control frame')

        return WsFrame(
            fin=fin,
            opcode=opcode,
            payload=payload,
            rsv1=rsv1,
            rsv2=rsv2,
            rsv3=rsv3,
        )
