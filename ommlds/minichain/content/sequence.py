"""
TODO:
 - track BlockContent nesting depth?
 - section names? dedicated 'section' content with header and body?
"""
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .content import Content
from .composite import CompositeContent


##


@dc.dataclass(frozen=True)
class SequenceContent(CompositeContent, lang.Abstract):
    l: ta.Sequence[Content]

    def child_content(self) -> ta.Sequence[Content]:
        return self.l


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
