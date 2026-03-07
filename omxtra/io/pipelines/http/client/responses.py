# ruff: noqa: UP006 UP045
# @omlish-lite
import typing as ta

from omlish.http.parsing import HttpParser

from ..aggregators import PipelineHttpObjectAggregatorDecoder
from ..decoders import PipelineHttpObjectDecoder
from ..decompressors import PipelineHttpObjectDecompressor
from ..responses import PipelineHttpResponseObjects


##


class PipelineHttpResponseDecoder(PipelineHttpResponseObjects, PipelineHttpObjectDecoder):
    _parse_mode: ta.Final = HttpParser.Mode.RESPONSE
    _if_content_length_missing: ta.Final = 'eof'


##


class PipelineHttpResponseAggregatorDecoder(
    PipelineHttpResponseObjects,
    PipelineHttpObjectAggregatorDecoder,
):
    _if_content_length_missing: ta.Final = 'eof'


##


class PipelineHttpResponseDecompressor(PipelineHttpResponseObjects, PipelineHttpObjectDecompressor):
    pass
