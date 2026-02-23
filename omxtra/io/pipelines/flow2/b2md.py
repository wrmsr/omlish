# ruff: noqa: UP006 UP045
# @omlish-lite
import abc
import typing as ta

from omlish.io.streams.direct import DirectByteStreamBuffer
from omlish.io.streams.scanning import ScanningByteStreamBuffer
from omlish.io.streams.segmented import SegmentedByteStreamBuffer
from omlish.io.streams.types import ByteStreamBuffer
from omlish.io.streams.types import MutableByteStreamBuffer
from omlish.io.streams.utils import ByteStreamBuffers
from omlish.lite.abstract import Abstract
from omlish.lite.check import check

from ..bytes.buffering import InboundBytesBufferingChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext
from ..core import ChannelPipelineMessages
from ..errors import DecodingChannelPipelineError
from .types import ChannelPipelineFlow
from .types import ChannelPipelineFlowMessages


##


class BytesToMessageDecoder(InboundBytesBufferingChannelPipelineHandler, Abstract):
    def __init__(
            self,
            *,
            scanning: bool = False,
    ) -> None:
        super().__init__()

        self._scanning = scanning

    def inbound_buffered_bytes(self) -> int:
        if (buf := self._buf) is None:
            return 0
        return len(buf)

    @abc.abstractmethod
    def _decode(
            self,
            ctx: ChannelPipelineHandlerContext,
            buf: ByteStreamBuffer,
            *,
            final: bool = False,
    ) -> ta.Iterable[ta.Any]:
        raise NotImplementedError

    #

    _buf: ta.Optional[MutableByteStreamBuffer] = None

    def _new_buf(self) -> MutableByteStreamBuffer:
        buf: MutableByteStreamBuffer = SegmentedByteStreamBuffer(chunk_size=0x4000)

        if self._scanning:
            buf = ScanningByteStreamBuffer(buf)

        return buf

    #

    _called_decode: bool = False  # ~ `selfFiredChannelRead`
    _produced_messages: bool = False  # ~ `firedChannelRead`

    def _call_decode(
            self,
            ctx: ChannelPipelineHandlerContext,
            buf: ByteStreamBuffer,
            *,
            final: bool = False,
    ) -> None:
        self._called_decode = True

        try:
            out = list(self._decode(ctx, buf, final=final))
        except DecodingChannelPipelineError:
            raise
        except Exception as e:
            raise DecodingChannelPipelineError from e

        if not out:
            return

        self._produced_messages = True

        for out_msg in out:
            ctx.feed_in(out_msg)

    #

    def _on_flush_input(self, ctx: ChannelPipelineHandlerContext) -> None:
        if (
                self._called_decode and
                not self._produced_messages and
                not ctx.channel.services[ChannelPipelineFlow].is_auto_read
        ):
            ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())

        self._called_decode = False
        self._produced_messages = False

        ctx.feed_in(ChannelPipelineFlowMessages.FlushInput())

    def _on_final_input(self, ctx: ChannelPipelineHandlerContext, msg: ChannelPipelineMessages.FinalInput) -> None:
        dec_buf: ByteStreamBuffer
        if self._buf is not None:
            dec_buf = self._buf
        else:
            dec_buf = DirectByteStreamBuffer(b'')

        self._call_decode(ctx, dec_buf, final=True)

        ctx.feed_in(msg)

    def _on_bytes_input(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        check.arg(len(msg) > 0)

        if self._buf is None:
            self._buf = self._new_buf()

        for seg in ByteStreamBuffers.iter_segments(msg):
            self._buf.write(seg)

        self._call_decode(ctx, self._buf)

    #

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineFlowMessages.FlushInput):
            self._on_flush_input(ctx)

        elif isinstance(msg, ChannelPipelineMessages.FinalInput):
            self._on_final_input(ctx, msg)

        elif ByteStreamBuffers.can_bytes(msg):
            self._on_bytes_input(ctx, msg)

        else:
            ctx.feed_in(msg)


##


@ta.final
class FnBytesToMessageDecoder(BytesToMessageDecoder):
    class DecodeFn(ta.Protocol):
        def __call__(
                self,
                ctx: ChannelPipelineHandlerContext,
                buf: ByteStreamBuffer,
                *,
                final: bool = False,
        ) -> ta.Iterable[ta.Any]:
            ...

    def __init__(
            self,
            decode_fn: DecodeFn,
            *,
            scanning: bool = False,
    ) -> None:
        super().__init__(
            scanning=scanning,
        )

        self._decode_fn = decode_fn

    def _decode(
            self,
            ctx: ChannelPipelineHandlerContext,
            buf: ByteStreamBuffer,
            *,
            final: bool = False,
    ) -> ta.Iterable[ta.Any]:
        return self._decode_fn(ctx, buf, final=final)
