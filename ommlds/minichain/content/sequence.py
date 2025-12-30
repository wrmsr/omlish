"""
TODO:
 - track BlockContent nesting depth?
 - section names? dedicated 'section' content with header and body?
"""
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .content import Content
from .standard import StandardContent


##


@dc.dataclass(frozen=True)
class SequenceContent(StandardContent, lang.Abstract):
    l: ta.Sequence[Content]


@dc.dataclass(frozen=True)
class InlineContent(SequenceContent, lang.Final):
    pass


@dc.dataclass(frozen=True)
class BlockContent(SequenceContent, lang.Final):
    pass


@dc.dataclass(frozen=True)
class ItemListContent(SequenceContent, lang.Final):
    _: dc.KW_ONLY

    style: ta.Literal['-', '#'] = '-'
