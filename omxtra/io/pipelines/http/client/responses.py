# ruff: noqa: UP006 UP045
# @omlish-lite
import typing as ta

from omlish.http.headers import HttpHeaders
from omlish.http.parsing import HttpParser
from omlish.http.parsing import ParsedHttpMessage
from omlish.io.streams.types import BytesLikeOrMemoryview
from omlish.lite.check import check

from ...bytes.buffering import InboundBytesBufferingChannelPipelineHandler
from ...core import ChannelPipelineHandlerContext
from ...core import ChannelPipelineMessages
from ..aggregators import PipelineHttpObjectAggregator
from ..decoders import PipelineHttpObjectDecoder
from ..objects import PipelineHttpMessageHead
from ..responses import FullPipelineHttpResponse
from ..responses import PipelineHttpResponseAborted
from ..responses import PipelineHttpResponseContentChunkData
from ..responses import PipelineHttpResponseEnd
from ..responses import PipelineHttpResponseHead


##


class PipelineHttpResponseDecoder(PipelineHttpObjectDecoder):
    _parse_mode: ta.Final[HttpParser.Mode] = HttpParser.Mode.RESPONSE

    def _make_head(self, parsed: ParsedHttpMessage) -> ta.Any:
        status = check.not_none(parsed.status_line)

        return PipelineHttpResponseHead(
            version=status.http_version,
            status=status.status_code,
            reason=status.reason_phrase,
            headers=HttpHeaders(parsed.headers.entries),
            parsed=parsed,
        )

    def _make_aborted(self, reason: str) -> ta.Any:
        return PipelineHttpResponseAborted(reason)

    def _make_content_chunk_data(self, data: BytesLikeOrMemoryview) -> ta.Any:
        return PipelineHttpResponseContentChunkData(data)

    def _make_end(self) -> ta.Any:
        return PipelineHttpResponseEnd()


##


class PipelineHttpResponseAggregator(
    InboundBytesBufferingChannelPipelineHandler,
    PipelineHttpObjectAggregator,
):
    _head_type: ta.Final[ta.Type[PipelineHttpResponseHead]] = PipelineHttpResponseHead
    _content_chunk_data_type: ta.Final[ta.Type[PipelineHttpResponseContentChunkData]] = PipelineHttpResponseContentChunkData  # noqa
    _end_type: ta.Final[ta.Type[PipelineHttpResponseEnd]] = PipelineHttpResponseEnd
    _final_type: ta.Final[type] = ChannelPipelineMessages.FinalInput

    def _make_aborted(self, reason: str) -> PipelineHttpResponseAborted:
        return PipelineHttpResponseAborted(reason)

    def _make_full(self, head: PipelineHttpMessageHead, body: BytesLikeOrMemoryview) -> FullPipelineHttpResponse:
        return FullPipelineHttpResponse(check.isinstance(head, PipelineHttpResponseHead), body)

    #

    def inbound_buffered_bytes(self) -> int:
        return self.buffered_bytes()

    #

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        self._handle(ctx, msg, ctx.feed_in)
