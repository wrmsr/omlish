"""
Open-container state.

Containers hold other blocks. CommonMark has two container kinds (excluding the extensions we punt): blockquotes and
lists. Lists themselves are containers of items; items are containers of arbitrary blocks. So the stack shape for `> 1.
foo` is:

    [OpenBlockQuote, OpenList(ordered, '.', 1), OpenItem(content_indent=3)]

Cf. pulldown-cmark/src/firstpass.rs::FirstPass - pulldown stores containers as tree nodes with `ItemBody::BlockQuote` /
`ItemBody::List` / `ItemBody::ListItem`; we store them as Python objects on a stack. Continuation handling and the
"scan_containers" walk are the same algorithm.
"""
from omlish import dataclasses as dc
from omlish import lang

from ..events import BlockQuoteKind


##


class OpenContainer(lang.Abstract):
    """Marker base for open container state. Variants are independent frozen dataclasses."""


@dc.dataclass(frozen=True)
class OpenBlockQuote(OpenContainer):
    """
    A blockquote - continuation marker is `>` (optionally indented up to 3 spaces). Cf.
    pulldown-cmark/src/scanners.rs::LineStart::scan_blockquote_marker. `kind` is set on the open event for GFM
    admonition tags (`[!NOTE]` etc.) and carried here so the close event matches.
    """

    open_start: int
    kind: BlockQuoteKind | None = None


@dc.dataclass(frozen=True)
class OpenList(OpenContainer):
    """
    A list. Has no continuation marker of its own - it stays open as long as its items continue or another item of the
    same kind opens. Cf. pulldown-cmark/src/parse.rs::ItemBody::List.

    Tight / loose tracking: `had_blank` is set true when a blank line is processed while this list is open, and reset to
    false when content is then added (at which point `is_loose` is set true). Cf.
    pulldown-cmark/src/parse.rs::surgerize_tight_list, which does the equivalent post-pass on the built tree.
    """

    is_ordered: bool
    marker_char: str  # '-', '+', '*', '.', or ')'
    start: int        # start number (ordered) or 0 (unordered)
    open_start: int   # offset of the first item's first non-indent char
    had_blank: bool = False
    is_loose: bool = False


@dc.dataclass(frozen=True)
class OpenItem(OpenContainer):
    """
    A list item. The `content_indent` is the column count subsequent lines must be indented to in order to remain inside
    the item. Cf. pulldown-cmark/src/parse.rs::ItemBody::ListItem.
    """

    content_indent: int
    open_start: int  # offset of the marker
    open_next: int   # offset just past the marker line's newline
