"""
Inline-parser intermediate representation.

A block's inline content is first tokenized into a flat list of `InlineNode`s, then the emphasis delimiter algorithm
wraps paired `DelimNode`s into `EmphasisGroup`s, and finally the resolved node list is converted to events.

Nodes carry absolute source offsets so events can carry them too. They are mutable (the emphasis resolution rewrites the
list in place), but the events emitted at the end are immutable.

Cf. pulldown-cmark/src/parse.rs::ItemBody - same conceptual role, different shape (pulldown stores inlines in its block
tree as `Maybe*` placeholders that the inline pass mutates in place; we maintain a separate flat list per block).
"""
from omcore import dataclasses as dc
from omcore import lang

from ..events import LinkType


##


class InlineNode(lang.Abstract):
    """
    Marker base for inline IR nodes. Concrete subclasses are mutable dataclasses (the emphasis resolution rewrites
    positions and group contents in place); we keep them as `lang.Abstract` siblings rather than a union alias to stay
    consistent with the rest of the project.
    """


@dc.dataclass()
class TextNode(InlineNode):
    offset: tuple[int, int]
    text: str


@dc.dataclass()
class CodeNode(InlineNode):
    offset: tuple[int, int]
    text: str


@dc.dataclass()
class HtmlNode(InlineNode):
    """
    Inline HTML span - emitted as `InlineHtml`. Distinguished from `HtmlBlock` (the leaf-block event) by source context,
    not by node type.
    """

    offset: tuple[int, int]
    text: str


@dc.dataclass()
class AutolinkNode(InlineNode):
    offset: tuple[int, int]
    target: str      # URI / email (no `mailto:` prefix added here; renderer handles it)
    is_email: bool


@dc.dataclass()
class SoftBreakNode(InlineNode):
    offset: tuple[int, int]


@dc.dataclass()
class HardBreakNode(InlineNode):
    offset: tuple[int, int]


@dc.dataclass()
class DelimNode(InlineNode):
    """
    An unresolved emphasis delimiter run. After tokenization the emphasis algorithm walks the node list, pairs
    DelimNodes (or leaves them as text), and replaces matched pairs with `EmphasisGroup`s.

    Cf. pulldown-cmark/src/parse.rs::InlineStack - same role; we store can_open / can_close directly instead of
    computing them at scan time.
    """

    offset: tuple[int, int]
    char: str        # '*' or '_'
    count: int       # number of consecutive chars in the run
    can_open: bool
    can_close: bool


@dc.dataclass()
class EmphasisGroup(InlineNode):
    """
    A resolved emphasis / strong / strikethrough group wrapping inner nodes.

    `kind` is one of `'emphasis'`, `'strong'`, or `'strikethrough'`. Nested emphasis (e.g. `***foo***` → strong inside
    emphasis) is just two nested EmphasisGroups.
    """

    offset: tuple[int, int]
    kind: str
    children: list[InlineNode]


@dc.dataclass()
class LinkOpenNode(InlineNode):
    """
    Placeholder for a `[` (link) or `![` (image) marker. Pairs with a LinkCloseNode during the link-resolution pass;
    unmatched openers fall back to text.
    """

    offset: tuple[int, int]
    is_image: bool


@dc.dataclass()
class LinkCloseNode(InlineNode):
    """
    Placeholder for a `]` and any immediately-following link-suffix syntax.

    `kind` is one of 'inline', 'reference', 'collapsed', or 'shortcut' - set by the tokenizer based on what immediately
    followed the `]` (`(...)`, `[label]`, `[]`, or nothing). For 'inline' the `dest_url` / `title` fields are populated;
    for 'reference' the `label` field is set; for 'collapsed' / 'shortcut' the label is derived from the inner text at
    resolution time.

    `consumed_end` is the absolute source offset just past the consumed link-suffix syntax (== the `]`'s own end
    position when no suffix was present).

    `raw_consumed` is the literal source text that was consumed (everything from the `]` through `consumed_end`). On
    resolution failure we emit this as plain text so consumed suffix syntax doesn't get lost - see CM Appendix A's rule
    about reconstituting "fake" link suffixes.
    """

    offset: tuple[int, int]
    consumed_end: int
    kind: str
    raw_consumed: str = ']'
    dest_url: str = ''
    title: str = ''
    label: str = ''


@dc.dataclass()
class LinkGroup(InlineNode):
    """
    A resolved link or image wrapping its text. The renderer turns this into Start/End(Link) or Start/End(Image) plus
    the children's events; for images the renderer flattens the children's text into the `alt` attribute.
    """

    offset: tuple[int, int]
    is_image: bool
    link_type: LinkType
    dest_url: str
    title: str
    id: str
    children: list[InlineNode]
