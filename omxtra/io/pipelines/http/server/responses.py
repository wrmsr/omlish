# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta

from omlish.lite.check import check

from ...core import ChannelPipelineHandler
from ...core import ChannelPipelineHandlerContext
from ..encoders import PipelineHttpEncoder
from ..encoders import PipelineHttpEncodingMessageAdapter
from ..objects import FullPipelineHttpMessage
from ..objects import PipelineHttpMessageContentChunkData
from ..objects import PipelineHttpMessageEnd
from ..objects import PipelineHttpMessageHead
from ..responses import FullPipelineHttpResponse
from ..responses import PipelineHttpResponseContentChunkData
from ..responses import PipelineHttpResponseEnd
from ..responses import PipelineHttpResponseHead
from ..responses import PipelineHttpResponseObject


##


class ResponsePipelineHttpEncodingMessageAdapter(PipelineHttpEncodingMessageAdapter):
    head_type: ta.Final[ta.Type[PipelineHttpMessageHead]] = PipelineHttpResponseHead
    full_type: ta.Final[ta.Type[FullPipelineHttpMessage]] = FullPipelineHttpResponse
    content_chunk_data_type: ta.Final[ta.Type[PipelineHttpMessageContentChunkData]] = PipelineHttpResponseContentChunkData  # noqa
    end_type: ta.Final[ta.Type[PipelineHttpMessageEnd]] = PipelineHttpResponseEnd

    def encode_head_line(self, head: PipelineHttpMessageHead) -> bytes:
        head = check.isinstance(head, PipelineHttpResponseHead)
        version_str = f'HTTP/{head.version.major}.{head.version.minor}'
        return f'{version_str} {head.status} {head.reason}\r\n'.encode('ascii')


##


class PipelineHttpResponseEncoder(ChannelPipelineHandler):
    def __init__(self) -> None:
        super().__init__()

        self._encoder = PipelineHttpEncoder(
            ResponsePipelineHttpEncodingMessageAdapter(),
        )

    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if not isinstance(msg, PipelineHttpResponseObject):
            ctx.feed_out(msg)
            return

        for out_msg in self._encoder.outbound(msg):
            ctx.feed_out(out_msg)
