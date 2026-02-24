# ruff: noqa: UP006 UP045
# @omlish-lite
import typing as ta
import zlib

from omlish.http.headers import HttpHeaders
from omlish.http.parsing import HttpParser
from omlish.http.parsing import ParsedHttpMessage
from omlish.io.streams.types import BytesLikeOrMemoryview
from omlish.io.streams.utils import ByteStreamBuffers
from omlish.lite.check import check

from ...bytes.buffering import InboundBytesBufferingChannelPipelineHandler
from ...core import ChannelPipelineHandler
from ...core import ChannelPipelineHandlerContext
from ...core import ChannelPipelineMessages
from ...flow.types import ChannelPipelineFlow
from ...flow.types import ChannelPipelineFlowMessages
from ..decoders import ChunkedPipelineHttpContentChunkDecoder
from ..decoders import PipelineHttpDecodingConfig
from ..decoders import PipelineHttpDecodingMessageAdapter
from ..decoders import PipelineHttpHeadDecoder
from ..responses import PipelineHttpResponseAborted
from ..responses import PipelineHttpResponseContentChunk
from ..responses import PipelineHttpResponseEnd
from ..responses import PipelineHttpResponseHead


##


class ResponsePipelineHttpDecodingMessageAdapter(PipelineHttpDecodingMessageAdapter):
    def make_head(self, parsed: ParsedHttpMessage) -> ta.Any:
        status = check.not_none(parsed.status_line)

        return PipelineHttpResponseHead(
            version=status.http_version,
            status=status.status_code,
            reason=status.reason_phrase,
            headers=HttpHeaders(parsed.headers.entries),
            parsed=parsed,
        )

    def make_aborted(self, reason: str) -> ta.Any:
        return PipelineHttpResponseAborted(reason)

    def make_chunk(self, data: BytesLikeOrMemoryview) -> ta.Any:
        return PipelineHttpResponseContentChunk(data)

    def make_end(self) -> ta.Any:
        return PipelineHttpResponseEnd()


##


class PipelineHttpResponseDecoder(InboundBytesBufferingChannelPipelineHandler):
    """HTTP/1.x response head decoder."""

    def __init__(
            self,
            *,
            config: PipelineHttpDecodingConfig = PipelineHttpDecodingConfig.DEFAULT,
    ) -> None:
        super().__init__()

        self._decoder = PipelineHttpHeadDecoder(
            ResponsePipelineHttpDecodingMessageAdapter(),
            HttpParser.Mode.RESPONSE,
            config=config,
        )

    def inbound_buffered_bytes(self) -> int:
        return self._decoder.inbound_buffered_bytes()

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if self._decoder.done:
            ctx.feed_in(msg)
            return

        if isinstance(msg, ChannelPipelineFlowMessages.FlushInput):
            if not ctx.services[ChannelPipelineFlow].is_auto_read():
                ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())

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
        if isinstance(msg, ChannelPipelineMessages.FinalInput):
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
            config: PipelineHttpDecodingConfig = PipelineHttpDecodingConfig.DEFAULT,
    ) -> None:
        super().__init__()

        self._config = config

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
                    ResponsePipelineHttpDecodingMessageAdapter(),
                    config=self._config,
                )

            ctx.feed_in(msg)
            return

        if (dec := self._decoder) is None:
            ctx.feed_in(msg)
            return

        if isinstance(msg, ChannelPipelineFlowMessages.FlushInput):
            if not ctx.services[ChannelPipelineFlow].is_auto_read():
                ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())

            ctx.feed_in(msg)
            return

        for dec_msg in dec.inbound(msg):
            ctx.feed_in(dec_msg)

        if dec.done:
            self._decoder = None
