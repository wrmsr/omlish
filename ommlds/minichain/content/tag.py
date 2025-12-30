"""
TODO:
 - track BlockContent nesting depth?
 - section names? dedicated 'section' content with header and body?
"""
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from .composite import CompositeContent
from .content import Content


##


@dc.dataclass(frozen=True)
class TagContent(CompositeContent, lang.Final):
    tag: str
    body: Content

    def child_content(self) -> ta.Sequence[Content]:
        return [self.body]

    def _replace_child_content(self, new_child_content: ta.Sequence[Content]) -> ta.Self:
        return self.replace(body=check.single(new_child_content))
