# ruff: noqa: UP006 UP007 UP045
# @om-lite
import os
import typing as ta

from ....io.pipelines.core import IoPipelineHandler
from ....io.pipelines.core import IoPipelineHandlerContext
from ....lite.bytes import bytes_like_to_bytes_strict
from ....lite.namespaces import NamespaceClass
from ..objects import IoPipelineHttpMessageBodyData
from ..requests import IoPipelineHttpRequestBodyData
from ..responses import IoPipelineHttpResponseBodyData
from .objects import IoPipelineWebsocketBinary
from .objects import IoPipelineWebsocketClose
from .objects import IoPipelineWebsocketFrame
from .objects import IoPipelineWebsocketOpcode
from .objects import IoPipelineWebsocketPing
from .objects import IoPipelineWebsocketPong
from .objects import IoPipelineWebsocketText


##


class IoPipelineWebsocketFrames(NamespaceClass):
    @staticmethod
    def mask_xor(data: bytes, key: bytes) -> bytes:
        out = bytearray(len(data))
        k0, k1, k2, k3 = key
        for i, b in enumerate(data):
            j = i & 3
            kb = k0 if j == 0 else k1 if j == 1 else k2 if j == 2 else k3
            out[i] = b ^ kb
        return bytes(out)


##


class IoPipelineWebsocketFrameEncoder(IoPipelineHandler):
    """Encodes WsFrame or high-level WsText/WsBinary/WsPing/WsPong/WsClose into bytes."""

    def __init__(self, *, mask: bool = False) -> None:
        super().__init__()

        self._mask = mask

    def outbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineWebsocketFrame):
            ctx.feed_out(self._encode_frame(msg, mask=self._mask))
            return

        if isinstance(msg, IoPipelineWebsocketText):
            frame = IoPipelineWebsocketFrame(
                fin=True,
                opcode=IoPipelineWebsocketOpcode.TEXT,
                payload=msg.text.encode('utf-8'),
            )
            ctx.feed_out(self._encode_frame(frame, mask=self._mask))
            return

        if isinstance(msg, IoPipelineWebsocketBinary):
            frame = IoPipelineWebsocketFrame(
                fin=True,
                opcode=IoPipelineWebsocketOpcode.BINARY,
                payload=msg.data,
            )
            ctx.feed_out(self._encode_frame(frame, mask=self._mask))
            return

        if isinstance(msg, IoPipelineWebsocketPing):
            frame = IoPipelineWebsocketFrame(
                fin=True,
                opcode=IoPipelineWebsocketOpcode.PING,
                payload=msg.data,
            )
            ctx.feed_out(self._encode_frame(frame, mask=self._mask))
            return

        if isinstance(msg, IoPipelineWebsocketPong):
            frame = IoPipelineWebsocketFrame(
                fin=True,
                opcode=IoPipelineWebsocketOpcode.PONG,
                payload=msg.data,
            )
            ctx.feed_out(self._encode_frame(frame, mask=self._mask))
            return

        if isinstance(msg, IoPipelineWebsocketClose):
            payload = b''
            if msg.code or msg.reason:
                payload = msg.code.to_bytes(2, 'big')
                if msg.reason:
                    payload += msg.reason.encode('utf-8')
            frame = IoPipelineWebsocketFrame(
                fin=True,
                opcode=IoPipelineWebsocketOpcode.CLOSE,
                payload=payload,
            )
            ctx.feed_out(self._encode_frame(frame, mask=self._mask))
            return

        ctx.feed_out(msg)

    def _encode_frame(self, frame: IoPipelineWebsocketFrame, *, mask: bool) -> bytes:
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
            payload = IoPipelineWebsocketFrames.mask_xor(payload, key)

        return bytes(h) + payload


class IoPipelineWebsocketClientFrameEncoder(IoPipelineWebsocketFrameEncoder):
    def __init__(self) -> None:
        super().__init__(mask=True)


class IoPipelineWebsocketServerFrameEncoder(IoPipelineWebsocketFrameEncoder):
    def __init__(self) -> None:
        super().__init__(mask=False)


##


class IoPipelineWebsocketFrameDecoder(IoPipelineHandler):
    """
    Decodes inbound bytes into WsFrame objects. If expect_masked is True/False, validates the MASK bit accordingly; if
    None, accepts either.
    """

    def __init__(
            self,
            *,
            expect_masked: bool,
            unwrap_message_body_cls: ta.Optional[ta.Type[IoPipelineHttpMessageBodyData]] = None,
    ) -> None:
        super().__init__()

        self._expect_mask = expect_masked
        self._unwrap_message_body_cls = unwrap_message_body_cls

        self._buf = bytearray()

    def _unwrap_message_bytes(self, msg: ta.Any) -> ta.Optional[bytes]:
        if isinstance(msg, (bytes, bytearray, memoryview)):
            return bytes(msg)

        if (mbc := self._unwrap_message_body_cls) is not None and isinstance(msg, mbc):
            return bytes_like_to_bytes_strict(msg.data)

        return None

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if (bs := self._unwrap_message_bytes(msg)) is not None:
            self._buf.extend(bs)
            self._drain(ctx)
            return

        ctx.feed_in(msg)

    def _drain(self, ctx: IoPipelineHandlerContext) -> None:
        while True:
            frm = self._try_parse_one()
            if frm is None:
                break
            ctx.feed_in(frm)

    def _try_parse_one(self) -> ta.Optional[IoPipelineWebsocketFrame]:
        b = self._buf
        if len(b) < 2:
            return None

        b0 = b[0]
        b1 = b[1]

        fin = bool(b0 & 0x80)
        rsv1 = bool(b0 & 0x40)
        rsv2 = bool(b0 & 0x20)
        rsv3 = bool(b0 & 0x10)
        opcode = IoPipelineWebsocketOpcode(b0 & 0x0F)

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
            payload = IoPipelineWebsocketFrames.mask_xor(payload, key)

        # Basic control-frame checks
        if opcode in (
            IoPipelineWebsocketOpcode.CLOSE,
            IoPipelineWebsocketOpcode.PING,
            IoPipelineWebsocketOpcode.PONG,
        ):
            if not fin or ln > 125:
                raise ValueError('invalid control frame')

        return IoPipelineWebsocketFrame(
            fin=fin,
            opcode=opcode,
            payload=payload,
            rsv1=rsv1,
            rsv2=rsv2,
            rsv3=rsv3,
        )


class IoPipelineWebsocketClientFrameDecoder(IoPipelineWebsocketFrameDecoder):
    def __init__(self) -> None:
        super().__init__(
            expect_masked=False,
            unwrap_message_body_cls=IoPipelineHttpResponseBodyData,
        )


class IoPipelineWebsocketServerFrameDecoder(IoPipelineWebsocketFrameDecoder):
    def __init__(self) -> None:
        super().__init__(
            expect_masked=True,
            unwrap_message_body_cls=IoPipelineHttpRequestBodyData,
        )
