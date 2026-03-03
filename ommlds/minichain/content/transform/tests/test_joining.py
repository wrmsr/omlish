import typing as ta

from ...containers import BlocksContent
from ...containers import ConcatContent
from ...containers import FlowContent
from ...content import Content
from ...text import TextContent
from ...visitors import ContentVisitor
from ..lift import LiftToStandardContentTransform


C = ta.TypeVar('C')
R = ta.TypeVar('R')


##


class JoiningContentVisitor(ContentVisitor[C, R]):
    def visit_text_content(self, c: TextContent, ctx: C) -> R:
        return self.visit_standard_content(c, ctx)

    def visit_flow_content(self, c: FlowContent, ctx: C) -> R:
        return self.visit_sequence_content(c, ctx)

    def visit_concat_content(self, c: ConcatContent, ctx: C) -> R:
        return self.visit_sequence_content(c, ctx)

    def visit_blocks_content(self, c: BlocksContent, ctx: C) -> R:
        return self.visit_sequence_content(c, ctx)


def test_joining():
    c: Content = ['hi', 'there']

    c = LiftToStandardContentTransform[None]().transform(c, None)
    print(c)
