# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta

from omlish.lite.check import check

from ..encoders import PipelineHttpObjectEncoder
from ..objects import PipelineHttpMessageHead
from ..responses import FullPipelineHttpResponse
from ..responses import PipelineHttpResponseContentChunkData
from ..responses import PipelineHttpResponseEnd
from ..responses import PipelineHttpResponseHead


##


class PipelineHttpResponseEncoder(PipelineHttpObjectEncoder):
    _head_type: ta.Final[ta.Type[PipelineHttpResponseHead]] = PipelineHttpResponseHead
    _full_type: ta.Final[ta.Type[FullPipelineHttpResponse]] = FullPipelineHttpResponse
    _content_chunk_data_type: ta.Final[ta.Type[PipelineHttpResponseContentChunkData]] = PipelineHttpResponseContentChunkData  # noqa
    _end_type: ta.Final[ta.Type[PipelineHttpResponseEnd]] = PipelineHttpResponseEnd

    def _encode_head_line(self, head: PipelineHttpMessageHead) -> bytes:
        head = check.isinstance(head, PipelineHttpResponseHead)
        version_str = f'HTTP/{head.version.major}.{head.version.minor}'
        return f'{version_str} {head.status} {head.reason}\r\n'.encode('ascii')
