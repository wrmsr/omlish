import collections.abc
import typing as ta

from omlish import check
from omlish import lang

from ..composite import CompositeContent
from ..content import Content
from ..visitors import ContentVisitor
from .types import ContentTransform


C = ta.TypeVar('C')


##


class VisitorContentTransform(ContentVisitor[C, Content], ContentTransform[C], lang.Abstract):
    @ta.final
    def transform(self, c: Content, ctx: C) -> Content:
        """Final - must be identical to `visit`."""

        return self.visit(c, ctx)

    #

    def visit_content(self, c: Content, ctx: C) -> Content:
        return c

    def visit_sequence(self, c: ta.Sequence[Content], ctx: C) -> Content:
        return lang.map_preserve(lambda cc: self.visit(cc, ctx), c)

    def visit_composite_content(self, c: CompositeContent, ctx: C) -> Content:
        cc = c.child_content()
        ncc = self.visit_sequence(cc, ctx)
        nc = c.replace_child_content(check.isinstance(ncc, collections.abc.Sequence))
        return super().visit_composite_content(nc, ctx)
