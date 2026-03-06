# ruff: noqa: UP045
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
from ..requests import FullPipelineHttpRequest
from ..requests import PipelineHttpRequestAborted
from ..requests import PipelineHttpRequestContentChunkData
from ..requests import PipelineHttpRequestEnd
from ..requests import PipelineHttpRequestHead


##


class PipelineHttpRequestDecoder(PipelineHttpObjectDecoder):
    _parse_mode: ta.Final[HttpParser.Mode] = HttpParser.Mode.REQUEST

    def _make_head(self, parsed: ParsedHttpMessage) -> PipelineHttpRequestHead:
        request = check.not_none(parsed.request_line)

        return PipelineHttpRequestHead(
            method=request.method,
            target=check.not_none(request.request_target).decode('utf-8'),
            version=request.http_version,
            headers=HttpHeaders(parsed.headers.entries),
            parsed=parsed,
        )

    def _make_aborted(self, reason: str) -> ta.Any:
        return PipelineHttpRequestAborted(reason)

    def _make_content_chunk_data(self, data: BytesLikeOrMemoryview) -> ta.Any:
        return PipelineHttpRequestContentChunkData(data)

    def _make_end(self) -> ta.Any:
        return PipelineHttpRequestEnd()


##


class PipelineHttpRequestAggregator(
    InboundBytesBufferingChannelPipelineHandler,
    PipelineHttpObjectAggregator,
):
    _head_type: ta.Final[ta.Type[PipelineHttpRequestHead]] = PipelineHttpRequestHead
    _content_chunk_data_type: ta.Final[ta.Type[PipelineHttpRequestContentChunkData]] = PipelineHttpRequestContentChunkData  # noqa
    _end_type: ta.Final[ta.Type[PipelineHttpRequestEnd]] = PipelineHttpRequestEnd
    _final_type: ta.Final[type] = ChannelPipelineMessages.FinalInput

    def _make_aborted(self, reason: str) -> PipelineHttpRequestAborted:
        return PipelineHttpRequestAborted(reason)

    def _make_full(self, head: PipelineHttpMessageHead, body: BytesLikeOrMemoryview) -> FullPipelineHttpRequest:
        return FullPipelineHttpRequest(check.isinstance(head, PipelineHttpRequestHead), body)

    #

    def inbound_buffered_bytes(self) -> int:
        return self.buffered_bytes()

    #

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        self._handle(ctx, msg, ctx.feed_in)
