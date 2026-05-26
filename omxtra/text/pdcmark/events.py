"""
Events emitted by the parser and the tags that classify Start / End events.

Surface mirrors pulldown-cmark's `Event` / `Tag` ADT (see pulldown-cmark/src/lib.rs). We drop variants for the
extensions we don't support — math, definition lists, metadata blocks, container extensions, heading attributes,
wikilinks, super / subscript, footnotes (initial). We also drop pulldown's `TagEnd`: pulldown uses it as a memory
optimization (it has a static assertion that `TagEnd` stays at most two bytes), which we have no equivalent need for.
Our `End` event just carries the same `Tag` instance type as `Start`, and any close-time-only attribute lives as a
sentinel-defaulted field on the `Tag` itself (see `List.tight`).
"""
import enum
import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


# pulldown-cmark/src/lib.rs::LinkType
class LinkType(enum.Enum):
    INLINE = 'inline'
    REFERENCE = 'reference'
    REFERENCE_UNKNOWN = 'reference_unknown'
    COLLAPSED = 'collapsed'
    COLLAPSED_UNKNOWN = 'collapsed_unknown'
    SHORTCUT = 'shortcut'
    SHORTCUT_UNKNOWN = 'shortcut_unknown'
    AUTOLINK = 'autolink'
    EMAIL = 'email'


# pulldown-cmark/src/lib.rs::Alignment
class Alignment(enum.Enum):
    NONE = 'none'
    LEFT = 'left'
    CENTER = 'center'
    RIGHT = 'right'


# pulldown-cmark/src/lib.rs::BlockQuoteKind
class BlockQuoteKind(enum.Enum):
    NOTE = 'note'
    TIP = 'tip'
    IMPORTANT = 'important'
    WARNING = 'warning'
    CAUTION = 'caution'


##  Tags  ##


# Marker base for all element tags. Inheritance, not a TypeAlias union — we want isinstance(t, Tag) to mean something
# and the project preference is empty abstract bases for capability markers.
class Tag(lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Paragraph(Tag):
    pass


@dc.dataclass(frozen=True)
class Heading(Tag):
    level: int  # 1..6


@dc.dataclass(frozen=True)
class BlockQuote(Tag):
    kind: BlockQuoteKind | None = None  # GFM admonition; None = regular blockquote


@dc.dataclass(frozen=True)
class FencedCodeBlock(Tag):
    info: str  # the info string after the opening fence; may be empty


@dc.dataclass(frozen=True)
class IndentedCodeBlock(Tag):
    pass


@dc.dataclass(frozen=True)
class HtmlBlock(Tag):
    pass


@dc.dataclass(frozen=True)
class List(Tag):
    start: int | None = None   # ordered list start number; None means unordered
    tight: bool | None = None  # None at Start; bool at End — only authoritative on the End event


@dc.dataclass(frozen=True)
class Item(Tag):
    pass


@dc.dataclass(frozen=True)
class Table(Tag):
    alignments: ta.Sequence[Alignment]


@dc.dataclass(frozen=True)
class TableHead(Tag):
    pass


@dc.dataclass(frozen=True)
class TableRow(Tag):
    pass


@dc.dataclass(frozen=True)
class TableCell(Tag):
    pass


@dc.dataclass(frozen=True)
class Emphasis(Tag):
    pass


@dc.dataclass(frozen=True)
class Strong(Tag):
    pass


@dc.dataclass(frozen=True)
class Strikethrough(Tag):
    pass


@dc.dataclass(frozen=True)
class Link(Tag):
    link_type: LinkType
    dest_url: str
    title: str
    id: str


@dc.dataclass(frozen=True)
class Image(Tag):
    link_type: LinkType
    dest_url: str
    title: str
    id: str


##  Events  ##


# pulldown-cmark/src/lib.rs::Event
# We always carry source offsets on every event; pulldown gates this behind OffsetIter.
class Event(lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class _OffsetEvent(Event, lang.Abstract):
    offset: tuple[int, int]  # absolute byte range in the input stream


@dc.dataclass(frozen=True)
class Start(_OffsetEvent):
    tag: Tag


@dc.dataclass(frozen=True)
class End(_OffsetEvent):
    tag: Tag


@dc.dataclass(frozen=True)
class Text(_OffsetEvent):
    text: str


@dc.dataclass(frozen=True)
class Code(_OffsetEvent):
    text: str


@dc.dataclass(frozen=True)
class Html(_OffsetEvent):
    text: str


@dc.dataclass(frozen=True)
class InlineHtml(_OffsetEvent):
    text: str


@dc.dataclass(frozen=True)
class SoftBreak(_OffsetEvent):
    pass


@dc.dataclass(frozen=True)
class HardBreak(_OffsetEvent):
    pass


@dc.dataclass(frozen=True)
class Rule(_OffsetEvent):
    pass


@dc.dataclass(frozen=True)
class TaskListMarker(_OffsetEvent):
    checked: bool
