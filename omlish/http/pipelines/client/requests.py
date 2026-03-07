# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
from ....lite.check import check
from ..encoders import PipelineHttpObjectEncoder
from ..objects import PipelineHttpMessageHead
from ..requests import PipelineHttpRequestHead
from ..requests import PipelineHttpRequestObjects


##


class PipelineHttpRequestEncoder(PipelineHttpRequestObjects, PipelineHttpObjectEncoder):
    def _encode_head_line(self, head: PipelineHttpMessageHead) -> bytes:
        head = check.isinstance(head, PipelineHttpRequestHead)
        version_str = f'HTTP/{head.version.major}.{head.version.minor}'
        return f'{head.method} {head.target} {version_str}\r\n'.encode('ascii')
