# ruff: noqa: UP006 UP045
# @omlish-lite
import typing as ta
import zlib

from omlish.http.headers import HttpHeaders
from omlish.http.parsing import HttpParser
from omlish.http.parsing import ParsedHttpMessage
from omlish.io.streams.utils import ByteStreamBuffers
from omlish.lite.check import check

from ...bytes.buffering import InboundBytesBufferingChannelPipelineHandler
from ...core import ChannelPipelineHandler
from ...core import ChannelPipelineHandlerContext
from ...core import ChannelPipelineMessages
from ..decoders import ChunkedPipelineHttpContentChunkDecoder
from ..decoders import PipelineHttpHeadDecoder
from ..responses import PipelineHttpResponseAborted
from ..responses import PipelineHttpResponseContentChunk
from ..responses import PipelineHttpResponseEnd
from ..responses import PipelineHttpResponseHead


##


class PipelineHttpResponseDecoder(InboundBytesBufferingChannelPipelineHandler):
    """HTTP/1.x response head decoder."""

    def __init__(
            self,
            *,
            max_head: int = 0x10000,
            buffer_chunk_size: int = 0x10000,
    ) -> None:
        super().__init__()

        self._decoder = PipelineHttpHeadDecoder(
            HttpParser.Mode.RESPONSE,
            lambda parsed: self._build_head(parsed),
            lambda reason: PipelineHttpResponseAborted(reason),
            max_head=max_head,
            buffer_chunk_size=buffer_chunk_size,
        )

    def inbound_buffered_bytes(self) -> int:
        return self._decoder.inbound_buffered_bytes()

    def _build_head(self, parsed: ParsedHttpMessage) -> PipelineHttpResponseHead:
        status = check.not_none(parsed.status_line)

        return PipelineHttpResponseHead(
            version=status.http_version,
            status=status.status_code,
            reason=status.reason_phrase,
            headers=HttpHeaders(parsed.headers.entries),
            parsed=parsed,
        )

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if self._decoder.done:
            ctx.feed_in(msg)
            return

        for dec_msg in self._decoder.inbound(msg):
            ctx.feed_in(dec_msg)


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

    # FIXME:
    #  - we get obj.unconsumed_tail and unused_data, but not the full internal buffer sizes
    # def inbound_buffered_bytes(self) -> int:

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
            out = self._z.decompress(mv)  # FIXME: max_length!! zip bombs
            # FIXME: also unconsumed_tail lol
            if out:
                ctx.feed_in(out)


##


class PipelineHttpResponseChunkedDecoder(InboundBytesBufferingChannelPipelineHandler):
    def __init__(
            self,
            *,
            max_chunk_header: int = 1024,
            buffer_chunk_size: int = 0x10000,
    ) -> None:
        super().__init__()

        self._max_chunk_header = max_chunk_header
        self._buffer_chunk_size = buffer_chunk_size

        self._decoder: ta.Optional[ChunkedPipelineHttpContentChunkDecoder] = None

    def inbound_buffered_bytes(self) -> ta.Optional[int]:
        if (dec := self._decoder) is None:
            return 0
        return dec.inbound_buffered_bytes()

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, PipelineHttpResponseHead):
            check.none(self._decoder)

            if msg.headers.contains_value('transfer-encoding', 'chunked', ignore_case=True):
                self._decoder = ChunkedPipelineHttpContentChunkDecoder(
                    lambda data: PipelineHttpResponseContentChunk(data),
                    lambda: PipelineHttpResponseEnd(),
                    lambda reason: PipelineHttpResponseAborted(reason),
                    max_chunk_header=self._max_chunk_header,
                    buffer_chunk_size=self._buffer_chunk_size,
                )

            ctx.feed_in(msg)
            return

        if (dec := self._decoder) is None:
            ctx.feed_in(msg)
            return

        for dec_msg in dec.inbound(msg):
            ctx.feed_in(dec_msg)

        if dec.done:
            self._decoder = None
