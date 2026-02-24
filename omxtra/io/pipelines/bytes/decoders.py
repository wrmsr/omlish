# ruff: noqa: FURB188 UP045
# @omlish-lite
"""
TODO:
 - netty 'pending_removal' trick
"""
import abc
import typing as ta

from omlish.io.streams.direct import DirectByteStreamBuffer
from omlish.io.streams.framing import LongestMatchDelimiterByteStreamFrameDecoder
from omlish.io.streams.scanning import ScanningByteStreamBuffer
from omlish.io.streams.segmented import SegmentedByteStreamBuffer
from omlish.io.streams.types import ByteStreamBuffer
from omlish.io.streams.types import MutableByteStreamBuffer
from omlish.io.streams.utils import ByteStreamBuffers
from omlish.lite.abstract import Abstract
from omlish.lite.check import check

from ..core import ChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext
from ..core import ChannelPipelineMessages
from ..errors import DecodingChannelPipelineError
from ..errors import IncompleteDecodingChannelPipelineError
from ..flow.types import ChannelPipelineFlow
from ..flow.types import ChannelPipelineFlowMessages
from .buffering import InboundBytesBufferingChannelPipelineHandler


##


class UnicodeDecoderChannelPipelineHandler(ChannelPipelineHandler):
    """bytes/view -> str (UTF-8, replacement)."""

    def __init__(
            self,
            encoding: str = 'utf-8',
            *,
            errors: ta.Literal['strict', 'ignore', 'replace'] = 'strict',
    ) -> None:
        super().__init__()

        self._encoding = encoding
        self._errors = errors

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if ByteStreamBuffers.can_bytes(msg):
            b = ByteStreamBuffers.any_to_bytes(msg)

            msg = b.decode(self._encoding, errors=self._errors)

        ctx.feed_in(msg)


##


class DelimiterFrameDecoderChannelPipelineHandler(InboundBytesBufferingChannelPipelineHandler):
    """
    bytes-like -> frames using longest-match delimiter semantics.

    TODO:
     - flow control, *or* replace with BytesToMessageDecoderChannelPipelineHandler
    """

    def __init__(
            self,
            delims: ta.Sequence[bytes],
            *,
            keep_ends: bool = False,
            max_size: ta.Optional[int] = None,
            max_buffer: ta.Optional[int] = None,
            buffer_chunk_size: int = 0x10000,
            on_incomplete_final: ta.Literal['allow', 'raise'] = 'allow',
    ) -> None:
        super().__init__()

        self._on_incomplete_final = on_incomplete_final

        self._buf = ScanningByteStreamBuffer(SegmentedByteStreamBuffer(
            max_size=max_buffer,
            chunk_size=buffer_chunk_size,
        ))

        self._fr = LongestMatchDelimiterByteStreamFrameDecoder(
            delims,
            keep_ends=keep_ends,
            max_size=max_size,
        )

    def inbound_buffered_bytes(self) -> int:
        return len(self._buf)

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineMessages.FinalInput):
            self._produce_frames(ctx, final=True)
            ctx.feed_in(msg)
            return

        if not ByteStreamBuffers.can_bytes(msg):
            ctx.feed_in(msg)
            return

        for mv in ByteStreamBuffers.iter_segments(msg):
            if mv:
                self._buf.write(mv)

        self._produce_frames(ctx)

    def _produce_frames(self, ctx: ChannelPipelineHandlerContext, *, final: bool = False) -> None:
        frames = self._fr.decode(self._buf, final=final)

        if final and len(self._buf):
            if (oif := self._on_incomplete_final) == 'allow':
                frames.append(self._buf.split_to(len(self._buf)))
            elif oif == 'raise':
                raise IncompleteDecodingChannelPipelineError
            else:
                raise RuntimeError(f'unexpected on_incomplete_final: {oif!r}')

        for fr in frames:
            ctx.feed_in(fr)


##


class BytesToMessageDecoderChannelPipelineHandler(InboundBytesBufferingChannelPipelineHandler, Abstract):
    def __init__(
            self,
            *,
            max_buffer_size: ta.Optional[int] = None,
            buffer_chunk_size: int = 0x10000,
            scanning_buffer: bool = False,
    ) -> None:
        super().__init__()

        self._max_buffer_size = max_buffer_size
        self._buffer_chunk_size = buffer_chunk_size
        self._scanning_buffer = scanning_buffer

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
        buf: MutableByteStreamBuffer = SegmentedByteStreamBuffer(
            max_size=self._max_buffer_size,
            chunk_size=self._buffer_chunk_size,
        )

        if self._scanning_buffer:
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
                not ctx.services[ChannelPipelineFlow].is_auto_read()
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


#


@ta.final
class FnBytesToMessageDecoderChannelPipelineHandler(BytesToMessageDecoderChannelPipelineHandler):
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
            max_buffer_size: ta.Optional[int] = None,
            buffer_chunk_size: int = 0x10000,
            scanning_buffer: bool = False,
    ) -> None:
        super().__init__(
            max_buffer_size=max_buffer_size,
            buffer_chunk_size=buffer_chunk_size,
            scanning_buffer=scanning_buffer,
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
