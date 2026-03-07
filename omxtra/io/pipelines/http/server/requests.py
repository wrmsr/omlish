# ruff: noqa: UP045
# @omlish-lite
import typing as ta

from omlish.http.parsing import HttpParser

from ...bytes.buffering import InboundBytesBufferingChannelPipelineHandler
from ...core import ChannelPipelineHandlerContext
from ...core import ChannelPipelineMessages
from ..aggregators import PipelineHttpObjectAggregator
from ..decoders import PipelineHttpObjectDecoder
from ..decompressors import PipelineHttpObjectDecompressor
from ..requests import PipelineHttpRequestObjects


##


class PipelineHttpRequestDecoder(PipelineHttpRequestObjects, PipelineHttpObjectDecoder):
    _parse_mode: ta.Final[HttpParser.Mode] = HttpParser.Mode.REQUEST
    _if_content_length_missing: ta.Final[ta.Literal['none']] = 'none'


##


class PipelineHttpRequestAggregatorDecoder(
    PipelineHttpRequestObjects,
    InboundBytesBufferingChannelPipelineHandler,
    PipelineHttpObjectAggregator,
):
    _if_content_length_missing: ta.Final[ta.Literal['none']] = 'none'
    _final_type: ta.Final[type] = ChannelPipelineMessages.FinalInput

    #

    def inbound_buffered_bytes(self) -> int:
        return self.buffered_bytes()

    #

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        self._handle(ctx, msg, ctx.feed_in)


##


class PipelineHttpRequestDecompressor(PipelineHttpRequestObjects, PipelineHttpObjectDecompressor):
    pass
