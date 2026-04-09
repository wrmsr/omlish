# ruff: noqa: FURB188 UP006 UP045
# @omlish-lite
"""
TODO:
 - netty 'pending_removal' trick
"""
import abc
import collections
import typing as ta

from ....lite.abstract import Abstract
from ....lite.check import check
from ...streams.direct import DirectByteStreamBuffer
from ...streams.framing import LongestMatchDelimiterByteStreamFrameDecoder
from ...streams.scanning import ScanningByteStreamBuffer
from ...streams.segmented import SegmentedByteStreamBuffer
from ...streams.types import ByteStreamBuffer
from ...streams.types import MutableByteStreamBuffer
from ...streams.utils import ByteStreamBuffers
from ...streams.utils import CanByteStreamBuffer
from ..core import IoPipelineHandler
from ..core import IoPipelineHandlerContext
from ..core import IoPipelineMessages
from ..errors import IncompleteDecodingIoPipelineError
from ..flow.types import IoPipelineFlow
from ..flow.types import IoPipelineFlowMessages
from .buffering import InboundBytesBufferingIoPipelineHandler


##


class UnicodeDecoderIoPipelineHandler(IoPipelineHandler):
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

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if ByteStreamBuffers.can_bytes(msg):
            b = ByteStreamBuffers.to_bytes(msg)

            msg = b.decode(self._encoding, errors=self._errors)

        ctx.feed_in(msg)


##


class DelimiterFrameDecoderIoPipelineHandler(InboundBytesBufferingIoPipelineHandler):
    """
    bytes-like -> frames using longest-match delimiter semantics.

    TODO:
     - flow control, *or* replace with BytesToMessageDecoderIoPipelineHandler
    """

    def __init__(
            self,
            delims: ta.Sequence[bytes],
            *,
            keep_ends: bool = False,
            max_size: ta.Optional[int] = None,
            max_buffer: ta.Optional[int] = None,
            buffer_chunk_size: int = 64 * 1024,
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

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineMessages.FinalInput):
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

    def _produce_frames(self, ctx: IoPipelineHandlerContext, *, final: bool = False) -> None:
        frames = self._fr.decode(self._buf, final=final)

        if final and len(self._buf):
            if (oif := self._on_incomplete_final) == 'allow':
                frames.append(self._buf.split_to(len(self._buf)))
            elif oif == 'raise':
                raise IncompleteDecodingIoPipelineError
            else:
                raise RuntimeError(f'unexpected on_incomplete_final: {oif!r}')

        for fr in frames:
            ctx.feed_in(fr)


##


class BytesToMessageDecoderIoPipelineHandler(IoPipelineHandler, Abstract):
    @abc.abstractmethod
    def _decode(
            self,
            ctx: IoPipelineHandlerContext,
            data: CanByteStreamBuffer,
            out: ta.List[ta.Any],
            *,
            final: bool = False,
    ) -> None:
        raise NotImplementedError

    #

    _decode_state: ta.Literal['ready', 'decoding'] = 'ready'

    _allow_decode_reentrance: bool = False
    _decode_output: ta.Optional['collections.deque[ta.Any]'] = None
    _decode_pending_input: ta.Optional['collections.deque[ta.Any]'] = None

    _called_decode: bool = False  # ~ `selfFiredChannelRead`
    _produced_messages: bool = False  # ~ `firedChannelRead`

    def _call_decode(
            self,
            ctx: IoPipelineHandlerContext,
            data: CanByteStreamBuffer,
            *,
            final: bool = False,
    ) -> None:
        if self._decode_state == 'ready':
            check.none(self._decode_output)
            check.none(self._decode_pending_input)

            self._decode_state = 'decoding'
            doq: 'collections.deque[ta.Any]' = collections.deque()
            diq: 'collections.deque[ta.Any]' = collections.deque()
            self._decode_output = doq
            self._decode_pending_input = diq

            self._called_decode = True

            try:
                out: ta.List[ta.Any] = []
                self._decode(ctx, data, out, final=final)
                doq.extend(out)

                if not doq:
                    return

                self._produced_messages = True

                while doq:
                    out_msg = doq.popleft()
                    ctx.feed_in(out_msg)

            finally:
                self._decode_output = None
                self._decode_pending_input = None
                self._decode_state = 'ready'

                while diq:
                    in_msg = diq.popleft()
                    self.inbound(ctx, in_msg)

        elif self._decode_state == 'decoding':
            if not self._allow_decode_reentrance:
                raise RuntimeError('already decoding')

            doq = check.not_none(self._decode_output)

            out = []
            self._decode(ctx, data, out, final=final)
            doq.extend(out)

        else:
            raise RuntimeError(f'unexpected decode state: {self._decode_state!r}')

    #

    def _on_bytes_input(self, ctx: IoPipelineHandlerContext, data: CanByteStreamBuffer) -> None:
        check.arg(len(data) > 0)

        self._call_decode(ctx, data)

    def _on_flush_input(self, ctx: IoPipelineHandlerContext) -> None:
        if (
                self._called_decode and
                not self._produced_messages and
                not ctx.services[IoPipelineFlow].is_auto_read()
        ):
            ctx.feed_out(IoPipelineFlowMessages.ReadyForInput())

        self._called_decode = False
        self._produced_messages = False

        ctx.feed_in(IoPipelineFlowMessages.FlushInput())

    def _on_final_input(self, ctx: IoPipelineHandlerContext, msg: IoPipelineMessages.FinalInput) -> None:
        self._call_decode(ctx, DirectByteStreamBuffer(b''), final=True)

        ctx.feed_in(msg)

    #

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineFlowMessages.FlushInput):
            if (diq := self._decode_pending_input) is not None:
                diq.append(msg)
            else:
                self._on_flush_input(ctx)

        elif isinstance(msg, IoPipelineMessages.FinalInput):
            if (diq := self._decode_pending_input) is not None:
                diq.append(msg)
            else:
                self._on_final_input(ctx, msg)

        elif ByteStreamBuffers.can_bytes(msg):
            self._on_bytes_input(ctx, msg)

        else:
            ctx.feed_in(msg)


#


@ta.final
class FnBytesToMessageDecoderIoPipelineHandler(BytesToMessageDecoderIoPipelineHandler):
    class DecodeFn(ta.Protocol):
        def __call__(
                self,
                ctx: IoPipelineHandlerContext,
                data: CanByteStreamBuffer,
                out: ta.List[ta.Any],
                *,
                final: bool = False,
        ) -> None:
            ...

    def __init__(
            self,
            decode_fn: DecodeFn,
    ) -> None:
        super().__init__()

        self._decode_fn = decode_fn

    def _decode(
            self,
            ctx: IoPipelineHandlerContext,
            buf: CanByteStreamBuffer,
            out: ta.List[ta.Any],
            *,
            final: bool = False,
    ) -> None:
        self._decode_fn(ctx, buf, out, final=final)


##


class BufferedBytesToMessageDecoderIoPipelineHandler(
    InboundBytesBufferingIoPipelineHandler,
    BytesToMessageDecoderIoPipelineHandler,
    Abstract,
):
    def __init__(
            self,
            *,
            max_buffer_size: ta.Optional[int] = None,
            buffer_chunk_size: int = 64 * 1024,
            scanning_buffer: bool = False,
    ) -> None:
        super().__init__()

        self._max_buffer_size = max_buffer_size
        self._buffer_chunk_size = buffer_chunk_size
        self._scanning_buffer = scanning_buffer

    #

    def inbound_buffered_bytes(self) -> int:
        if (buf := self._buf) is None:
            return 0
        return len(buf)

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

    def _decode(
            self,
            ctx: IoPipelineHandlerContext,
            data: CanByteStreamBuffer,
            out: ta.List[ta.Any],
            *,
            final: bool = False,
    ) -> None:
        if final:
            check.arg(len(data) == 0)

            if not isinstance(data, ByteStreamBuffer):
                data = DirectByteStreamBuffer(b'')

            self._decode_buffer(ctx, data, out, final=final)

            return

        check.arg(len(data) > 0)

        if (buf := self._buf) is None:
            buf = self._buf = self._new_buf()

        for seg in ByteStreamBuffers.iter_segments(data):
            buf.write(seg)

        self._decode_buffer(ctx, buf, out, final=final)

    #

    @abc.abstractmethod
    def _decode_buffer(
            self,
            ctx: IoPipelineHandlerContext,
            buf: ByteStreamBuffer,
            out: ta.List[ta.Any],
            *,
            final: bool = False,
    ) -> None:
        raise NotImplementedError
