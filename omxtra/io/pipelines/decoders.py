# ruff: noqa: FURB188 UP045
# @omlish-lite
import typing as ta

from omlish.io.streams.framing import LongestMatchDelimiterByteStreamFrameDecoder
from omlish.io.streams.scanning import ScanningByteStreamBuffer
from omlish.io.streams.segmented import SegmentedByteStreamBuffer
from omlish.io.streams.utils import ByteStreamBuffers

from .core import ChannelPipelineHandler
from .core import ChannelPipelineHandlerContext
from .core import ChannelPipelineMessages
from .errors import IncompleteDecodingChannelPipelineError


##


class UnicodePipelineDecoder(ChannelPipelineHandler):
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

            if (bfc := ctx.bytes_flow_control) is not None:
                bfc.on_consumed(self, len(b))

            msg = b.decode(self._encoding, errors=self._errors)

        ctx.feed_in(msg)


class DelimiterFramePipelineDecoder(ChannelPipelineHandler):  # HasChannelPipelineFlowBuffer
    """bytes-like -> frames using longest-match delimiter semantics."""

    def __init__(
            self,
            delims: ta.Sequence[bytes],
            *,
            keep_ends: bool = False,
            max_size: ta.Optional[int] = None,
            max_buffer_bytes: ta.Optional[int] = None,
            chunk_size: int = 0x10000,
            on_incomplete_final: ta.Literal['allow', 'raise'] = 'allow',
    ) -> None:
        super().__init__()

        self._on_incomplete_final = on_incomplete_final

        self._buf = ScanningByteStreamBuffer(SegmentedByteStreamBuffer(
            max_bytes=max_buffer_bytes,
            chunk_size=chunk_size,
        ))

        self._fr = LongestMatchDelimiterByteStreamFrameDecoder(
            delims,
            keep_ends=keep_ends,
            max_size=max_size,
        )

    # @ta.override
    # def buffered_cost(self) -> int:
    #     return len(self._buf)

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineMessages.Eof):
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
        before = len(self._buf)

        frames = self._fr.decode(self._buf, final=final)

        if final and len(self._buf):
            if (oif := self._on_incomplete_final) == 'allow':
                frames.append(self._buf.split_to(len(self._buf)))
            elif oif == 'raise':
                raise IncompleteDecodingChannelPipelineError
            else:
                raise RuntimeError(f'unexpected on_incomplete_final: {oif!r}')

        after = len(self._buf)

        if (bfc := ctx.bytes_flow_control) is not None:
            bfc.on_consumed(self, before - after)

        for fr in frames:
            ctx.feed_in(fr)
