"""
TODO:
 - attribution
"""
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .content import Content
from .composite import CompositeContent


##


@dc.dataclass(frozen=True)
class QuoteContent(CompositeContent, lang.Final):
    body: Content

    def child_content(self) -> ta.Sequence[Content]:
        return [self.body]
