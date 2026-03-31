# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
from ....lite.check import check
from ..chunking import IoPipelineHttpObjectChunker
from ..compression.compressors import IoPipelineHttpObjectCompressor
from ..encoders import IoPipelineHttpObjectEncoder
from ..objects import IoPipelineHttpMessageHead
from ..responses import IoPipelineHttpResponseHead
from ..responses import IoPipelineHttpResponseObjects


##


class IoPipelineHttpResponseEncoder(IoPipelineHttpResponseObjects, IoPipelineHttpObjectEncoder):
    def _encode_head_line(self, head: IoPipelineHttpMessageHead) -> bytes:
        head = check.isinstance(head, IoPipelineHttpResponseHead)
        version_str = f'HTTP/{head.version.major}.{head.version.minor}'
        return f'{version_str} {head.status} {head.reason}\r\n'.encode('ascii')


##


class IoPipelineHttpResponseChunker(IoPipelineHttpResponseObjects, IoPipelineHttpObjectChunker):
    pass


##


class IoPipelineHttpResponseCompressor(IoPipelineHttpResponseObjects, IoPipelineHttpObjectCompressor):
    pass
