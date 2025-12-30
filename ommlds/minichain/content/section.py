import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from .composite import CompositeContent
from .content import Content


##


@dc.dataclass(frozen=True)
class SectionContent(CompositeContent, lang.Final):
    body: Content

    _: dc.KW_ONLY

    header: str | None

    def child_content(self) -> ta.Sequence[Content]:
        return [self.body]

    def _replace_child_content(self, new_child_content: ta.Sequence[Content]) -> ta.Self:
        return self.replace(body=check.single(new_child_content))
