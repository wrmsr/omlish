# ruff: noqa: FURB188
import typing as ta

from omlish.io.streams.framing import LongestMatchDelimiterByteStreamFramer
from omlish.io.streams.segmented import SegmentedByteStreamBuffer
from omlish.io.streams.utils import ByteStreamBuffers

from .core import ChannelPipelineEvents
from .core import ChannelPipelineHandler
from .core import ChannelPipelineHandlerContext


##


class Utf8Decode(ChannelPipelineHandler):
    """bytes/view -> str (UTF-8, replacement)."""

    def __init__(self, *, bytes_flow_control: bool = False) -> None:
        super().__init__()

        self._bytes_flow_control = bytes_flow_control

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if ByteStreamBuffers.can_bytes(msg):
            b = ByteStreamBuffers.to_bytes(msg)

            if self._bytes_flow_control and (fc := ctx.flow_control) is not None:
                fc.on_consumed(len(b))

            msg = b.decode('utf-8', errors='replace')

        ctx.feed_in(msg)


class StripLineEndings(ChannelPipelineHandler):
    """str line -> str without trailing CR (supports both LF and CRLF sources)."""

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, str):
            if msg.endswith('\r'):
                msg = msg[:-1]

        ctx.feed_in(msg)


class DelimiterFrameDecoder(ChannelPipelineHandler):  # HasChannelPipelineFlowBuffer
    """bytes-like -> frames using longest-match delimiter semantics."""

    def __init__(
            self,
            delims: ta.Sequence[bytes],
            *,
            keep_ends: bool = False,
            max_size: int | None = None,
            max_buffer_bytes: int | None = None,
            chunk_size: int = 0x4000,
            bytes_flow_control: bool = False,
    ) -> None:
        super().__init__()

        self._bytes_flow_control = bytes_flow_control

        self._buf = SegmentedByteStreamBuffer(
            max_bytes=max_buffer_bytes,
            chunk_size=chunk_size,
        )

        self._fr = LongestMatchDelimiterByteStreamFramer(
            delims,
            keep_ends=keep_ends,
            max_size=max_size,
        )

    # @ta.override
    # def buffered_cost(self) -> int:
    #     return len(self._buf)

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineEvents.Eof):
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
        after = len(self._buf)

        if self._bytes_flow_control and (fc := ctx.flow_control) is not None:
            fc.on_consumed(before - after)

        for fr in frames:
            ctx.feed_in(fr)
