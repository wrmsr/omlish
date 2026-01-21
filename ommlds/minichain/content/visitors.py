import collections.abc
import inspect
import typing as ta

from omlish import collections as col
from omlish import lang

from .code import BlockCodeContent
from .code import CodeContent
from .code import InlineCodeContent
from .composite import CompositeContent
from .content import BaseContent
from .content import Content
from .dynamic import DynamicContent
from .emphasis import BoldContent
from .emphasis import BoldItalicContent
from .emphasis import EmphasisContent
from .emphasis import ItalicContent
from .images import ImageContent
from .json import JsonContent
from .link import LinkContent
from .markdown import MarkdownContent
from .namespaces import NamespaceContent
from .placeholders import PlaceholderContent
from .quote import QuoteContent
from .recursive import RecursiveContent
from .resources import ResourceContent
from .section import SectionContent
from .sequence import BlockContent
from .sequence import InlineContent
from .sequence import ItemListContent
from .sequence import SequenceContent
from .standard import StandardContent
from .tag import TagContent
from .templates import TemplateContent
from .text import TextContent


C = ta.TypeVar('C')
R = ta.TypeVar('R')


##


class ContentVisitor(lang.Abstract, ta.Generic[C, R]):
    _visit_method_map: ta.ClassVar[ta.Mapping[ta.Any, str]]

    def visit(self, c: Content, ctx: C) -> R:
        if isinstance(c, str):
            return self.visit_str(c, ctx)

        if isinstance(c, collections.abc.Sequence):
            return self.visit_sequence(c, ctx)

        try:
            a = self._visit_method_map[type(c)]
        except KeyError:
            raise TypeError(c) from None

        return getattr(self, a)(c, ctx)

    ##
    # per-type visit methods

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

    ##
    # StandardContent

    def visit_standard_content(self, c: StandardContent, ctx: C) -> R:
        return self.visit_base_content(c, ctx)

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

    def visit_composite_content(self, c: CompositeContent, ctx: C) -> R:
        return self.visit_standard_content(c, ctx)

    def visit_section_content(self, c: SectionContent, ctx: C) -> R:
        return self.visit_composite_content(c, ctx)

    def visit_tag_content(self, c: TagContent, ctx: C) -> R:
        return self.visit_composite_content(c, ctx)

    ##
    # CodeContent

    def visit_code_content(self, c: CodeContent, ctx: C) -> R:
        return self.visit_standard_content(c, ctx)

    def visit_inline_code_content(self, c: InlineCodeContent, ctx: C) -> R:
        return self.visit_code_content(c, ctx)

    def visit_block_code_content(self, c: BlockCodeContent, ctx: C) -> R:
        return self.visit_code_content(c, ctx)

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

    def visit_resource_content(self, c: ResourceContent, ctx: C) -> R:
        return self.visit_recursive_content(c, ctx)

    def visit_template_content(self, c: TemplateContent, ctx: C) -> R:
        return self.visit_dynamic_content(c, ctx)

    ##
    # EmphasisContent

    def visit_emphasis_content(self, c: EmphasisContent, ctx: C) -> R:
        return self.visit_standard_content(c, ctx)

    def visit_bold_content(self, c: BoldContent, ctx: C) -> R:
        return self.visit_emphasis_content(c, ctx)

    def visit_italic_content(self, c: ItalicContent, ctx: C) -> R:
        return self.visit_emphasis_content(c, ctx)

    def visit_bold_italic_content(self, c: BoldItalicContent, ctx: C) -> R:
        return self.visit_emphasis_content(c, ctx)

    ##
    # SequenceContent

    def visit_sequence_content(self, c: SequenceContent, ctx: C) -> R:
        return self.visit_composite_content(c, ctx)

    def visit_inline_content(self, c: InlineContent, ctx: C) -> R:
        return self.visit_sequence_content(c, ctx)

    def visit_block_content(self, c: BlockContent, ctx: C) -> R:
        return self.visit_sequence_content(c, ctx)

    def visit_item_list_content(self, c: ItemListContent, ctx: C) -> R:
        return self.visit_sequence_content(c, ctx)


ContentVisitor._visit_method_map = col.make_map([  # noqa
    (list(inspect.signature(o).parameters.values())[1].annotation, a)
    for a, o in ContentVisitor.__dict__.items()
    if a.startswith('visit_')
], strict=True)


##


class StandardContentVisitorTypeError(TypeError):
    pass


class StandardContentVisitor(ContentVisitor[C, R], lang.Abstract):
    def visit_str(self, c: str, ctx: C) -> R:
        raise StandardContentVisitorTypeError(c)

    def visit_sequence(self, c: ta.Sequence[Content], ctx: C) -> R:
        raise StandardContentVisitorTypeError(c)


##


class StaticContentVisitorTypeError(TypeError):
    pass


class StaticContentVisitor(ContentVisitor[C, R], lang.Abstract):
    def visit_dynamic_content(self, c: DynamicContent, ctx: C) -> R:
        raise StaticContentVisitorTypeError(c)
