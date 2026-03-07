# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
from ....lite.check import check
from ..encoders import IoPipelineHttpObjectEncoder
from ..objects import IoPipelineHttpMessageHead
from ..requests import IoPipelineHttpRequestHead
from ..requests import IoPipelineHttpRequestObjects


##


class IoPipelineHttpRequestEncoder(IoPipelineHttpRequestObjects, IoPipelineHttpObjectEncoder):
    def _encode_head_line(self, head: IoPipelineHttpMessageHead) -> bytes:
        head = check.isinstance(head, IoPipelineHttpRequestHead)
        version_str = f'HTTP/{head.version.major}.{head.version.minor}'
        return f'{head.method} {head.target} {version_str}\r\n'.encode('ascii')
