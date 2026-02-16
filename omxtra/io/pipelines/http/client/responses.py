# ruff: noqa: UP006 UP045
# @omlish-lite
import typing as ta
import zlib

from omlish.http.headers import HttpHeaders
from omlish.http.parsing import HttpParser
from omlish.http.parsing import ParsedHttpMessage
from omlish.io.streams.utils import ByteStreamBuffers
from omlish.lite.check import check

from ...core import ChannelPipelineHandler
from ...core import ChannelPipelineHandlerContext
from ...core import ChannelPipelineMessages
from ..decoders import PipelineHttpChunkedDecoder
from ..decoders import PipelineHttpHeadDecoder
from ..responses import PipelineHttpResponseContentChunk
from ..responses import PipelineHttpResponseEnd
from ..responses import PipelineHttpResponseHead


##


class PipelineHttpResponseDecoder(PipelineHttpHeadDecoder):
    """
    HTTP/1.x response head decoder.

    Extends PipelineHttpHeadDecoder to parse status line (version, status, reason) + headers.
    """

    def _parse_mode(self) -> HttpParser.Mode:
        return HttpParser.Mode.RESPONSE

    def _build_head(self, parsed: ParsedHttpMessage) -> PipelineHttpResponseHead:
        status = check.not_none(parsed.status_line)

        return PipelineHttpResponseHead(
            version=status.http_version,
            status=status.status_code,
            reason=status.reason_phrase,
            headers=HttpHeaders(parsed.headers.entries),
            parsed=parsed,
        )


##


class PipelineHttpResponseConditionalGzipDecoder(ChannelPipelineHandler):
    """
    Conditional streaming gzip decompression.

    Watches for DecodedHttpResponseHead; if Content-Encoding includes 'gzip', enable zlib decompressor for body bytes.
    Flushes on EOF.
    """

    def __init__(self) -> None:
        super().__init__()

        self._enabled = False
        self._z: ta.Optional[ta.Any] = None

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineMessages.Eof):
            if self._enabled and self._z is not None:
                tail = self._z.flush()
                if tail:
                    ctx.feed_in(tail)
            ctx.feed_in(msg)
            return

        if isinstance(msg, PipelineHttpResponseHead):
            enc = msg.headers.lower.get('content-encoding', ())
            self._enabled = 'gzip' in enc
            self._z = zlib.decompressobj(16 + zlib.MAX_WBITS) if self._enabled else None
            ctx.feed_in(msg)
            return

        if (
                not self._enabled or
                self._z is None or
                not ByteStreamBuffers.can_bytes(msg)
        ):
            ctx.feed_in(msg)
            return

        for mv in ByteStreamBuffers.iter_segments(msg):
            out = self._z.decompress(mv)
            if out:
                ctx.feed_in(out)


##


class PipelineHttpResponseChunkedDecoder(PipelineHttpChunkedDecoder):
    """
    HTTP/1.x response chunked transfer encoding decoder.

    Extends PipelineHttpChunkedDecoder to decode chunked response bodies.
    """

    def _is_head_message(self, msg: ta.Any) -> bool:
        return isinstance(msg, PipelineHttpResponseHead)

    def _should_enable(self, head: ta.Any) -> bool:
        te = head.headers.lower.get('transfer-encoding', ())
        return 'chunked' in te

    def _emit_chunk(self, ctx: ChannelPipelineHandlerContext, chunk_data: ta.Any) -> None:
        data = ByteStreamBuffers.any_to_bytes(chunk_data)
        ctx.feed_in(PipelineHttpResponseContentChunk(data))

    def _emit_end(self, ctx: ChannelPipelineHandlerContext) -> None:
        ctx.feed_in(PipelineHttpResponseEnd())
