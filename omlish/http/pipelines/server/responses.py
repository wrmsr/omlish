# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
from ....lite.check import check
from ..encoders import PipelineHttpObjectEncoder
from ..objects import PipelineHttpMessageHead
from ..responses import PipelineHttpResponseHead
from ..responses import PipelineHttpResponseObjects


##


class PipelineHttpResponseEncoder(PipelineHttpResponseObjects, PipelineHttpObjectEncoder):
    def _encode_head_line(self, head: PipelineHttpMessageHead) -> bytes:
        head = check.isinstance(head, PipelineHttpResponseHead)
        version_str = f'HTTP/{head.version.major}.{head.version.minor}'
        return f'{version_str} {head.status} {head.reason}\r\n'.encode('ascii')
