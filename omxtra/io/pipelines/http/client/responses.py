# ruff: noqa: UP006 UP045
# @omlish-lite
import typing as ta

from omlish.http.parsing import HttpParser

from ...bytes.buffering import InboundBytesBufferingChannelPipelineHandler
from ...core import ChannelPipelineHandlerContext
from ...core import ChannelPipelineMessages
from ..aggregators import PipelineHttpObjectAggregator
from ..decoders import PipelineHttpObjectDecoder
from ..responses import PipelineHttpResponseObjects
from ..decompressors import PipelineHttpObjectDecompressor


##


class PipelineHttpResponseDecoder(PipelineHttpResponseObjects, PipelineHttpObjectDecoder):
    _parse_mode: ta.Final[HttpParser.Mode] = HttpParser.Mode.RESPONSE
    _if_content_length_missing: ta.Final[ta.Literal['eof']] = 'eof'


##


class PipelineHttpResponseAggregatorDecoder(
    PipelineHttpResponseObjects,
    InboundBytesBufferingChannelPipelineHandler,
    PipelineHttpObjectAggregator,
):
    _if_content_length_missing: ta.Final[ta.Literal['eof']] = 'eof'
    _final_type: ta.Final[type] = ChannelPipelineMessages.FinalInput

    #

    def inbound_buffered_bytes(self) -> int:
        return self.buffered_bytes()

    #

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        self._handle(ctx, msg, ctx.feed_in)


##


class PipelineHttpResponseDecompressor(PipelineHttpResponseObjects, PipelineHttpObjectDecompressor):
    pass
