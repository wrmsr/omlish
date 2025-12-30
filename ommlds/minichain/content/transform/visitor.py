import typing as ta

from omlish import lang

from ..code import CodeContent
from ..content import BaseContent
from ..content import Content
from ..content import LeafContent
from ..dynamic import DynamicContent
from ..images import ImageContent
from ..json import JsonContent
from ..markdown import MarkdownContent
from ..namespaces import NamespaceContent
from ..placeholders import PlaceholderContent
from ..quote import QuoteContent
from ..recursive import RecursiveContent
from ..section import SectionContent
from ..sequence import BlockContent
from ..sequence import InlineContent
from ..sequence import ItemListContent
from ..sequence import SequenceContent
from ..standard import StandardContent
from ..tag import TagContent
from ..templates import TemplateContent
from ..text import TextContent


C = ta.TypeVar('C')
R = ta.TypeVar('R')


##


class ContentVisitor(lang.Abstract, ta.Generic[C, R]):
    def visit_content(self, c: Content, ctx: C) -> R:
        raise TypeError(c)

    ##
    # non-BaseContent

    def visit_str(self, c: str, ctx: C) -> R:
        return self.visit_content(c, ctx)

    def visit_sequence(self, c: ta.Sequence[Content], ctx: C) -> R:
        return self.visit_content(c, ctx)

    ##
    # BaseContent

    def visit_base_content(self, c: BaseContent, ctx: C) -> R:
        return self.visit_content(c, ctx)

    def visit_leaf_content(self, c: LeafContent, ctx: C) -> R:
        return self.visit_base_content(c, ctx)

    ##
    # StandardContent

    def visit_standard_content(self, c: StandardContent, ctx: C) -> R:
        if isinstance(c, LeafContent):
            return self.visit_leaf_content(c, ctx)
        else:
            return self.visit_base_content(c, ctx)

    ##
    # final StandardContent

    def visit_code_content(self, c: CodeContent, ctx: C) -> R:
        return self.visit_standard_content(c, ctx)

    def visit_image_content(self, c: ImageContent, ctx: C) -> R:
        return self.visit_standard_content(c, ctx)

    def visit_json_content(self, c: JsonContent, ctx: C) -> R:
        return self.visit_standard_content(c, ctx)

    def visit_markdown_content(self, c: MarkdownContent, ctx: C) -> R:
        return self.visit_standard_content(c, ctx)

    def visit_quote_content(self, c: QuoteContent, ctx: C) -> R:
        return self.visit_standard_content(c, ctx)

    def visit_section_content(self, c: SectionContent, ctx: C) -> R:
        return self.visit_standard_content(c, ctx)

    def visit_tag_content(self, c: TagContent, ctx: C) -> R:
        return self.visit_standard_content(c, ctx)

    def visit_text_content(self, c: TextContent, ctx: C) -> R:
        return self.visit_standard_content(c, ctx)

    ##
    # DynamicContent

    def visit_dynamic_content(self, c: DynamicContent, ctx: C) -> R:
        return self.visit_standard_content(c, ctx)

    def visit_recursive_content(self, c: RecursiveContent, ctx: C) -> R:
        return self.visit_dynamic_content(c, ctx)

    def visit_namespace_content(self, c: NamespaceContent, ctx: C) -> R:
        return self.visit_recursive_content(c, ctx)

    def visit_placeholder_content(self, c: PlaceholderContent, ctx: C) -> R:
        return self.visit_recursive_content(c, ctx)

    def visit_template_content(self, c: TemplateContent, ctx: C) -> R:
        return self.visit_dynamic_content(c, ctx)

    ##
    # SequenceContent

    def visit_sequence_content(self, c: SequenceContent, ctx: C) -> R:
        return self.visit_standard_content(c, ctx)

    def visit_inline_content(self, c: InlineContent, ctx: C) -> R:
        return self.visit_sequence_content(c, ctx)

    def visit_block_content(self, c: BlockContent, ctx: C) -> R:
        return self.visit_sequence_content(c, ctx)

    def visit_item_list_content(self, c: ItemListContent, ctx: C) -> R:
        return self.visit_sequence_content(c, ctx)
