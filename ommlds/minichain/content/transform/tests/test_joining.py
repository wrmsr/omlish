import typing as ta

from ...section import SectionContent
from ...sequence import BlocksContent
from ...sequence import ConcatContent
from ...sequence import FlowContent
from ...text import TextContent
from ...visitors import ContentVisitor


C = ta.TypeVar('C')
R = ta.TypeVar('R')


##


class JoiningContentVisitor(ContentVisitor[C, R]):
    def visit_text_content(self, c: TextContent, ctx: C) -> R:
        return self.visit_standard_content(c, ctx)

    def visit_section_content(self, c: SectionContent, ctx: C) -> R:
        return self.visit_composite_content(c, ctx)

    def visit_flow_content(self, c: FlowContent, ctx: C) -> R:
        return self.visit_sequence_content(c, ctx)

    def visit_concat_content(self, c: ConcatContent, ctx: C) -> R:
        return self.visit_sequence_content(c, ctx)

    def visit_blocks_content(self, c: BlocksContent, ctx: C) -> R:
        return self.visit_sequence_content(c, ctx)
