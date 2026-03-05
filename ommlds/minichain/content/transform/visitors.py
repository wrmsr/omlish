import collections.abc
import typing as ta

from omlish import check
from omlish import lang

from ..composite import CompositeContent
from ..content import Content
from ..visitors import ContentVisitor
from .types import ContentTransform


##


class VisitorContentTransform(ContentVisitor[None, Content], ContentTransform, lang.Abstract):
    @ta.final
    def transform(self, c: Content) -> Content:
        """Final - must be identical to `visit`."""

        return self.visit(c, None)

    #

    def visit_content(self, c: Content, ctx: None) -> Content:
        return c

    def visit_sequence(self, c: ta.Sequence[Content], ctx: None) -> Content:
        return lang.map_preserve(lambda cc: self.visit(cc, ctx), c)

    def visit_composite_content(self, c: CompositeContent, ctx: None) -> Content:
        cc = c.child_content()
        ncc = lang.map_preserve(lambda cc2: self.visit(cc2, ctx), cc)
        nc = c.replace_child_content(check.isinstance(ncc, collections.abc.Sequence))
        return super().visit_composite_content(nc, ctx)
