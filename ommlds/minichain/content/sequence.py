"""
TODO:
 - track BlockContent nesting depth?
 - section names? dedicated 'section' content with header and body?
"""
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .simple import SimpleExtendedContent
from .types import Content


##


@dc.dataclass(frozen=True)
class SequenceContent(SimpleExtendedContent, lang.Abstract):
    l: ta.Sequence[Content]


@dc.dataclass(frozen=True)
class InlineContent(SequenceContent, lang.Final):
    pass


@dc.dataclass(frozen=True)
class BlockContent(SequenceContent, lang.Final):
    pass
