# ruff: noqa: UP006
# @omlish-lite
from omlish.lite.abstract import Abstract

from ..core import ChannelPipelineHandler


##


class BytesToMessageDecoder(ChannelPipelineHandler, Abstract):
    pass
