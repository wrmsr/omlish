# ruff: noqa: UP045
# @omlish-lite
import typing as ta

from ...parsing import HttpParser
from ..aggregators import IoPipelineHttpObjectAggregatorDecoder
from ..chunking import IoPipelineHttpObjectDechunker
from ..compression.decompressors import IoPipelineHttpObjectDecompressor
from ..decoders import IoPipelineHttpObjectDecoder
from ..requests import IoPipelineHttpRequestObjects


##


class IoPipelineHttpRequestDecoder(IoPipelineHttpRequestObjects, IoPipelineHttpObjectDecoder):
    _parse_mode: ta.Final = HttpParser.Mode.REQUEST
    _if_content_length_missing: ta.Final = 'empty'


##


class IoPipelineHttpRequestAggregatorDecoder(
    IoPipelineHttpRequestObjects,
    IoPipelineHttpObjectAggregatorDecoder,
):
    _if_content_length_missing: ta.Final = 'empty'


##


class IoPipelineHttpRequestDechunker(IoPipelineHttpRequestObjects, IoPipelineHttpObjectDechunker):
    pass


##


class IoPipelineHttpRequestDecompressor(IoPipelineHttpRequestObjects, IoPipelineHttpObjectDecompressor):
    pass
