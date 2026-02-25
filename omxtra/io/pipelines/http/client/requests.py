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
from ..requests import FullPipelineHttpRequest
from ..requests import PipelineHttpRequestContentChunkData
from ..requests import PipelineHttpRequestEnd
from ..requests import PipelineHttpRequestHead
from ..requests import PipelineHttpRequestObject


##


class RequestPipelineHttpEncodingMessageAdapter(PipelineHttpEncodingMessageAdapter):
    head_type: ta.Final[ta.Type[PipelineHttpMessageHead]] = PipelineHttpRequestHead
    full_type: ta.Final[ta.Type[FullPipelineHttpMessage]] = FullPipelineHttpRequest
    content_chunk_data_type: ta.Final[ta.Type[PipelineHttpMessageContentChunkData]] = PipelineHttpRequestContentChunkData  # noqa
    end_type: ta.Final[ta.Type[PipelineHttpMessageEnd]] = PipelineHttpRequestEnd

    def encode_head_line(self, head: PipelineHttpMessageHead) -> bytes:
        head = check.isinstance(head, PipelineHttpRequestHead)
        version_str = f'HTTP/{head.version.major}.{head.version.minor}'
        return f'{head.method} {head.target} {version_str}\r\n'.encode('ascii')


##


class PipelineHttpRequestEncoder(ChannelPipelineHandler):
    def __init__(self) -> None:
        super().__init__()

        self._encoder = PipelineHttpEncoder(
            RequestPipelineHttpEncodingMessageAdapter(),
        )

    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if not isinstance(msg, PipelineHttpRequestObject):
            ctx.feed_out(msg)
            return

        for out_msg in self._encoder.outbound(msg):
            ctx.feed_out(out_msg)
