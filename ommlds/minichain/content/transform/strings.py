import typing as ta

from omlish import dataclasses as dc

from ..content import Content
from ..emphasis import EmphasisContent
from ..metadata import ContentOriginal
from ..text import TextContent
from .visitors import VisitorContentTransform


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
class StringFnContentTransform(VisitorContentTransform[None]):
    fn: ta.Callable[[str], str]

    def visit_str(self, c: str, ctx: None) -> TextContent:
        return TextContent(self.fn(c)).with_metadata(ContentOriginal(c))

    def visit_text_content(self, c: TextContent, ctx: None) -> TextContent:
        return c.replace(s=self.fn(c.s))

    def visit_emphasis_content(self, c: EmphasisContent, ctx: None) -> EmphasisContent:
        return c.replace(s=self.fn(c.s))


def transform_content_strings(fn: ta.Callable[[str], str], o: Content) -> Content:
    return StringFnContentTransform(fn).transform(o, None)
