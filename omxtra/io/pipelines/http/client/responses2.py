# ruff: noqa: UP006 UP045
# @omlish-lite
import typing as ta
import zlib

from omlish.io.streams.utils import ByteStreamBuffers

from ...core import ChannelPipelineHandler
from ...core import ChannelPipelineHandlerContext
from ...core import ChannelPipelineMessages
from ..responses import PipelineHttpResponseHead


##


class PipelineHttpResponseConditionalGzipDecoder2(ChannelPipelineHandler):
    """
    Conditional streaming gzip decompression.

    Watches for DecodedHttpResponseHead; if Content-Encoding includes 'gzip', enable zlib decompressor for body bytes.
    Flushes on EOF.
    """

    # Hard safety caps (tune to taste)
    MAX_DECOMP_CHUNK = 64 * 1024          # max bytes emitted per inflate step
    MAX_DECOMP_TOTAL = 256 * 1024 * 1024  # max total decompressed bytes per response
    MAX_EXPANSION_RATIO = 200             # max_out <= max(1, in_total) * ratio (+ small slack)

    def __init__(self) -> None:
        super().__init__()

        self._enabled = False
        self._z: ta.Optional[ta.Any] = None

        # accounting / limits
        self._in_total = 0
        self._out_total = 0
        self._pending_out = 0  # bytes produced but not yet ctx.feed_in()'d (usually 0 here)

    def inbound_buffered_bytes(self) -> int:
        # Conservative + observable.
        # NOTE: we intentionally cannot observe zlib's internal pending-output buffer size.
        z = self._z
        ut = 0
        if z is not None:
            try:
                ut = len(z.unconsumed_tail)  # visible compressed bytes retained by CPython wrapper
            except Exception:  # noqa
                ut = 0
        return self._pending_out + ut

    def _reset_limits(self) -> None:
        self._in_total = 0
        self._out_total = 0
        self._pending_out = 0

    def _check_budgets(self) -> None:
        # Absolute limit
        if self._out_total > self.MAX_DECOMP_TOTAL:
            raise ValueError('gzip decompressed output exceeds limit (possible zip bomb)')

        # Ratio limit (with a little slack so tiny inputs don't trip absurdly)
        # Slack is proportional to chunk size so streaming remains smooth.
        in_total = self._in_total
        slack = self.MAX_DECOMP_CHUNK
        if self._out_total > (max(1, in_total) * self.MAX_EXPANSION_RATIO + slack):
            raise ValueError('gzip expansion ratio exceeds limit (possible zip bomb)')

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineMessages.Eof):
            if self._enabled and self._z is not None:
                # Drain flush() output under the same chunking discipline.
                while True:
                    out = self._z.flush(self.MAX_DECOMP_CHUNK)
                    if not out:
                        break
                    self._out_total += len(out)
                    self._check_budgets()
                    ctx.feed_in(out)
            ctx.feed_in(msg)
            return

        if isinstance(msg, PipelineHttpResponseHead):
            enc = msg.headers.lower.get('content-encoding', ())
            self._enabled = 'gzip' in enc
            self._z = zlib.decompressobj(16 + zlib.MAX_WBITS) if self._enabled else None
            self._reset_limits()
            ctx.feed_in(msg)
            return

        if (
                not self._enabled or
                self._z is None or
                not ByteStreamBuffers.can_bytes(msg)
        ):
            ctx.feed_in(msg)
            return

        z = self._z

        for mv in ByteStreamBuffers.iter_segments(msg):
            # Track compressed bytes "offered" (good enough for ratio bounds; you said ignore tail mechanics for now)
            self._in_total += len(mv)

            # Stream out in bounded chunks so zlib can't accumulate huge pending output.
            # We do *not* consume unconsumed_tail in this implementation, per your note.
            while True:
                out = z.decompress(mv, self.MAX_DECOMP_CHUNK)
                if not out:
                    break
                self._out_total += len(out)
                self._check_budgets()
                ctx.feed_in(out)

                # IMPORTANT: don't loop forever on the same mv if zlib made progress only by returning output while not
                # consuming input; in practice, inflate will either consume input or eventually return b"" once its
                # output buffer is filled/drained. Because we pass max_length, each iteration is bounded.

            # FIXME: unconsumed_tail handling intentionally omitted per request
            # mv = z.unconsumed_tail  (etc.)
