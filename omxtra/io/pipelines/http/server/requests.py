# ruff: noqa: UP045
# @omlish-lite
import typing as ta

from omlish.http.parsing import HttpParser

from ..aggregators import PipelineHttpObjectAggregatorDecoder
from ..decoders import PipelineHttpObjectDecoder
from ..decompressors import PipelineHttpObjectDecompressor
from ..requests import PipelineHttpRequestObjects


##


class PipelineHttpRequestDecoder(PipelineHttpRequestObjects, PipelineHttpObjectDecoder):
    _parse_mode: ta.Final = HttpParser.Mode.REQUEST
    _if_content_length_missing: ta.Final = 'none'


##


class PipelineHttpRequestAggregatorDecoder(
    PipelineHttpRequestObjects,
    PipelineHttpObjectAggregatorDecoder,
):
    _if_content_length_missing: ta.Final = 'none'


##


class PipelineHttpRequestDecompressor(PipelineHttpRequestObjects, PipelineHttpObjectDecompressor):
    pass
