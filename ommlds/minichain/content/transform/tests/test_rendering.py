import typing as ta

from ...code import BlockCodeContent
from ...code import InlineCodeContent
from ...containers import BlocksContent
from ...containers import ConcatContent
from ...containers import FlowContent
from ...emphasis import BoldContent
from ...emphasis import BoldItalicContent
from ...emphasis import ItalicContent
from ...images import ImageContent
from ...itemlist import ItemListContent
from ...json import JsonContent
from ...link import LinkContent
from ...markdown import MarkdownContent
from ...quote import QuoteContent
from ...section import SectionContent
from ...tag import TagContent
from ...text import TextContent
from ...visitors import ContentVisitor


C = ta.TypeVar('C')
R = ta.TypeVar('R')


##


class RenderingContentVisitor(ContentVisitor[C, R]):
    ##
    # leaf StandardContent

    def visit_image_content(self, c: ImageContent, ctx: C) -> R:
        return self.visit_standard_content(c, ctx)

    def visit_json_content(self, c: JsonContent, ctx: C) -> R:
        return self.visit_standard_content(c, ctx)

    def visit_link_content(self, c: LinkContent, ctx: C) -> R:
        return self.visit_standard_content(c, ctx)

    def visit_markdown_content(self, c: MarkdownContent, ctx: C) -> R:
        return self.visit_standard_content(c, ctx)

    def visit_quote_content(self, c: QuoteContent, ctx: C) -> R:
        return self.visit_standard_content(c, ctx)

    def visit_text_content(self, c: TextContent, ctx: C) -> R:
        return self.visit_standard_content(c, ctx)

    ##
    # CompositeContent

    def visit_section_content(self, c: SectionContent, ctx: C) -> R:
        return self.visit_composite_content(c, ctx)

    def visit_tag_content(self, c: TagContent, ctx: C) -> R:
        return self.visit_composite_content(c, ctx)

    ##
    # CodeContent

    def visit_inline_code_content(self, c: InlineCodeContent, ctx: C) -> R:
        return self.visit_code_content(c, ctx)

    def visit_block_code_content(self, c: BlockCodeContent, ctx: C) -> R:
        return self.visit_code_content(c, ctx)

    ##
    # EmphasisContent

    def visit_bold_content(self, c: BoldContent, ctx: C) -> R:
        return self.visit_emphasis_content(c, ctx)

    def visit_italic_content(self, c: ItalicContent, ctx: C) -> R:
        return self.visit_emphasis_content(c, ctx)

    def visit_bold_italic_content(self, c: BoldItalicContent, ctx: C) -> R:
        return self.visit_emphasis_content(c, ctx)

    ##
    # SequenceContent

    def visit_item_list_content(self, c: ItemListContent, ctx: C) -> R:
        return self.visit_sequence_content(c, ctx)

    ##
    # ContainerContent

    def visit_flow_content(self, c: FlowContent, ctx: C) -> R:
        return self.visit_sequence_content(c, ctx)

    def visit_concat_content(self, c: ConcatContent, ctx: C) -> R:
        return self.visit_sequence_content(c, ctx)

    def visit_blocks_content(self, c: BlocksContent, ctx: C) -> R:
        return self.visit_sequence_content(c, ctx)
