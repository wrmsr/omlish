# ruff: noqa: UP045
# @omlish-lite
import typing as ta

from ...parsing import HttpParser
from ..aggregators import IoPipelineHttpObjectAggregatorDecoder
from ..decoders import IoPipelineHttpObjectDecoder
from ..decompressors import IoPipelineHttpObjectDecompressor
from ..requests import IoPipelineHttpRequestObjects


##


class IoPipelineHttpRequestDecoder(IoPipelineHttpRequestObjects, IoPipelineHttpObjectDecoder):
    _parse_mode: ta.Final = HttpParser.Mode.REQUEST
    _if_content_length_missing: ta.Final = 'none'


##


class IoPipelineHttpRequestAggregatorDecoder(
    IoPipelineHttpRequestObjects,
    IoPipelineHttpObjectAggregatorDecoder,
):
    _if_content_length_missing: ta.Final = 'none'


##


class IoPipelineHttpRequestDecompressor(IoPipelineHttpRequestObjects, IoPipelineHttpObjectDecompressor):
    pass
