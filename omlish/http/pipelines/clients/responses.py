# ruff: noqa: UP006 UP045
# @omlish-lite
import typing as ta

from ...parsing import HttpParser
from ..aggregators import IoPipelineHttpObjectAggregatorDecoder
from ..chunking import IoPipelineHttpObjectDechunker
from ..compression.decompressors import IoPipelineHttpObjectDecompressor
from ..decoders import IoPipelineHttpObjectDecoder
from ..responses import IoPipelineHttpResponseObjects


##


class IoPipelineHttpResponseDecoder(IoPipelineHttpResponseObjects, IoPipelineHttpObjectDecoder):
    _parse_mode: ta.Final = HttpParser.Mode.RESPONSE
    _if_content_length_missing: ta.Final = 'eof'


##


class IoPipelineHttpResponseAggregatorDecoder(
    IoPipelineHttpResponseObjects,
    IoPipelineHttpObjectAggregatorDecoder,
):
    _if_content_length_missing: ta.Final = 'eof'


##


class IoPipelineHttpResponseDechunker(IoPipelineHttpResponseObjects, IoPipelineHttpObjectDechunker):
    pass


##


class IoPipelineHttpResponseDecompressor(IoPipelineHttpResponseObjects, IoPipelineHttpObjectDecompressor):
    pass
