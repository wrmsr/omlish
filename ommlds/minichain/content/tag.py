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
class TagContent(CompositeContent, lang.Final):
    tag: str
    body: Content

    def child_content(self) -> ta.Sequence[Content]:
        return [self.body]
