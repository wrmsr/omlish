# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta

from omlish.lite.check import check

from ..encoders import PipelineHttpObjectEncoder
from ..objects import PipelineHttpMessageHead
from ..requests import FullPipelineHttpRequest
from ..requests import PipelineHttpRequestContentChunkData
from ..requests import PipelineHttpRequestEnd
from ..requests import PipelineHttpRequestHead


##


class PipelineHttpRequestEncoder(PipelineHttpObjectEncoder):
    _head_type: ta.Final[ta.Type[PipelineHttpRequestHead]] = PipelineHttpRequestHead
    _full_type: ta.Final[ta.Type[FullPipelineHttpRequest]] = FullPipelineHttpRequest
    _content_chunk_data_type: ta.Final[ta.Type[PipelineHttpRequestContentChunkData]] = PipelineHttpRequestContentChunkData  # noqa
    _end_type: ta.Final[ta.Type[PipelineHttpRequestEnd]] = PipelineHttpRequestEnd

    def _encode_head_line(self, head: PipelineHttpMessageHead) -> bytes:
        head = check.isinstance(head, PipelineHttpRequestHead)
        version_str = f'HTTP/{head.version.major}.{head.version.minor}'
        return f'{head.method} {head.target} {version_str}\r\n'.encode('ascii')
