"""
Event-driven HTML renderer.

Cf. pulldown-cmark/src/html.rs::HtmlWriter::run. Same event-loop shape; we differ in (a) writing to an in-memory
StringIO that the caller turns into a `str`, (b) buffering per list so that the `tight: bool` carried on the closing
`List` end-event can retroactively suppress `<p>` wrappers inside that list. Originally we always treats lists as loose
(`<p>` is emitted around item content); now we populate the tight flag and the renderer honors it.

The renderer escapes text content for HTML; raw HTML events (`Html`, `InlineHtml`) are written verbatim. Code-span text
gets HTML escape but not body-text-quote escape (matching pulldown).
"""
import io
import typing as ta

from ..events import Alignment
from ..events import BlockQuote
from ..events import Code
from ..events import Emphasis
from ..events import End
from ..events import Event
from ..events import FencedCodeBlock
from ..events import HardBreak
from ..events import Heading
from ..events import Html
from ..events import HtmlBlock
from ..events import Image
from ..events import IndentedCodeBlock
from ..events import InlineHtml
from ..events import Item
from ..events import Link
from ..events import List
from ..events import Paragraph
from ..events import Rule
from ..events import SoftBreak
from ..events import Start
from ..events import Strikethrough
from ..events import Strong
from ..events import Table
from ..events import TableCell
from ..events import TableHead
from ..events import TableRow
from ..events import Tag
from ..events import TaskListMarker
from ..events import Text


##


# pulldown-cmark-escape/src/lib.rs::escape_html / escape_html_body_text
def _escape_html(s: str) -> str:
    # Body text escape: `&`, `<`, `>`, `"`. We don't try to be smart about pre-escaped entities; the inline parser will
    # preserve them via dedicated Text/Html events.
    return (
        s
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
    )


_BLOCK_TAGS: tuple = (
    BlockQuote,
    FencedCodeBlock,
    IndentedCodeBlock,
    HtmlBlock,
    List,
    Item,
    Table,
    TableHead,
    TableRow,
    TableCell,
)


def _build_list_tight_map(events: list[Event]) -> dict[int, bool]:
    """
    Pre-pass over events. Returns a map from Start(List) event index to the tight bool read from the matching End(List).
    `None` (unresolved) treated as `False` for renderer purposes.
    """

    out: dict[int, bool] = {}
    stack: list[int] = []
    for i, ev in enumerate(events):
        if isinstance(ev, Start) and isinstance(ev.tag, List):
            stack.append(i)
        elif isinstance(ev, End) and isinstance(ev.tag, List) and stack:
            start_ix = stack.pop()
            out[start_ix] = bool(ev.tag.tight)
    return out


def _align_attr(align: Alignment) -> str:
    if align == Alignment.LEFT:
        return ' style="text-align: left"'
    if align == Alignment.CENTER:
        return ' style="text-align: center"'
    if align == Alignment.RIGHT:
        return ' style="text-align: right"'
    return ''


def _escape_href(s: str) -> str:
    """
    Encode a URL for safe inclusion in an HTML href / src attribute.

    Same character set as pulldown-cmark-escape's `escape_href`: most "safe" URL characters pass through; non-ASCII,
    controls, spaces, `"`, `\\`, `` ` ``, `[`, `]`, `<`, `>`, `^`, `|` get percent-encoded; pre-existing percent-escapes
    are left intact.
    """

    out: list[str] = []
    i = 0
    n = len(s)
    safe_punct = "!#$&'()*+,-./:;=?@_~"  # URL chars left untouched
    while i < n:
        c = s[i]
        if c == '%' and i + 2 < n and s[i + 1] in '0123456789abcdefABCDEF' and s[i + 2] in '0123456789abcdefABCDEF':
            # Pre-existing percent-escape — pass through.
            out.append(s[i:i + 3])
            i += 3
            continue
        if c == '&':
            out.append('&amp;')
            i += 1
            continue
        if c.isalnum() or c in safe_punct:
            out.append(c)
            i += 1
            continue
        # Percent-encode each UTF-8 byte.
        for b in c.encode('utf-8'):
            out.append(f'%{b:02X}')
        i += 1
    return ''.join(out)


##


def render_html(events: ta.Iterable[Event]) -> str:
    """Render an iterable of events to an HTML string."""

    return _HtmlRenderer().run(events)


class _HtmlRenderer:
    def __init__(self) -> None:
        super().__init__()
        self._buf = io.StringIO()
        self._end_newline = True
        # Block-container nesting + tight-list tracking. `_block_stack` holds the open block- container tags;
        # `_open_list_tight` is the parallel stack of tight values for the open Lists (pulled from the matching
        # End(List) via the pre-pass `_list_tight_map`). `_suppressed_paragraphs` is a per-Paragraph stack of "was this
        # Start suppressed?" bools so the End handler mirrors the decision.
        self._block_stack: list[Tag] = []
        self._open_list_tight: list[bool] = []
        self._suppressed_paragraphs: list[bool] = []
        self._list_tight_map: dict[int, bool] = {}
        # Pulldown emits Start(Image) with an unclosed `<img ... alt="` and then runs the inner text through
        # escape_html, swallowing nested Start/End tags. We do the same: when image nesting depth > 0, suppress nested
        # Start/End and gather Text events into the alt buffer.
        self._image_nesting = 0
        self._image_dest_url: list[str] = []   # stack — supports nested images
        self._image_title: list[str] = []
        self._image_alt_buf: list[list[str]] = []
        # Table state — pulldown-cmark/src/html.rs uses the same shape. Pushed on Start(Table), popped on End(Table);
        # supports nested tables (rare but legal).
        self._table_alignments: list[tuple] = []  # current table's alignments
        self._table_in_head: list[bool] = []      # True while inside TableHead
        self._table_cell_ix: list[int] = []       # column index within current row
        self._table_body_open: list[bool] = []    # True once we've emitted `<tbody>`

    def run(self, events: ta.Iterable[Event]) -> str:
        events_list = list(events)
        self._list_tight_map = _build_list_tight_map(events_list)
        for ix, ev in enumerate(events_list):
            self._dispatch(ev, ix)
        return self._buf.getvalue()

    def _is_in_tight_item(self) -> bool:
        return (
            bool(self._block_stack)
            and isinstance(self._block_stack[-1], Item)
            and bool(self._open_list_tight)
            and self._open_list_tight[-1]
        )

    def _write(self, s: str) -> None:
        if not s:
            return
        self._buf.write(s)
        self._end_newline = s.endswith('\n')

    def _newline(self) -> None:
        if not self._end_newline:
            self._buf.write('\n')
            self._end_newline = True

    def _dispatch(self, ev: Event, event_ix: int = 0) -> None:
        # Image alt-text mode: collect text content, suppress nested HTML emission.
        if self._image_nesting > 0 and not isinstance(ev, (Start, End)):
            self._absorb_into_alt(ev)
            return
        if isinstance(ev, Start):
            tag = ev.tag
            if isinstance(tag, Image):
                self._open_image(tag)
                return
            if self._image_nesting > 0:
                return
            # Tight-list `<p>` suppression: a Paragraph that's the direct child of an Item whose List is tight emits no
            # wrapper. We still push a sentinel so End(Paragraph) can mirror the decision.
            if isinstance(tag, Paragraph) and self._is_in_tight_item():
                self._suppressed_paragraphs.append(True)
                return
            # Push block tags onto the structural stack so the suppression check above works.
            if isinstance(tag, _BLOCK_TAGS):
                if isinstance(tag, List):
                    self._open_list_tight.append(self._list_tight_map.get(event_ix, False))
                self._block_stack.append(tag)
            if isinstance(tag, Paragraph):
                self._suppressed_paragraphs.append(False)
            self._start_tag(tag)
        elif isinstance(ev, End):
            tag = ev.tag
            if isinstance(tag, Image):
                self._close_image()
                return
            if self._image_nesting > 0:
                return
            if isinstance(tag, Paragraph):
                if self._suppressed_paragraphs and self._suppressed_paragraphs.pop():
                    return  # matching suppressed Start — emit no </p>
                self._end_tag(tag)
                return
            if isinstance(tag, _BLOCK_TAGS):
                if isinstance(tag, List):
                    self._open_list_tight.pop()
                self._block_stack.pop()
            self._end_tag(tag)
        elif isinstance(ev, Text):
            self._write(_escape_html(ev.text))
        elif isinstance(ev, Code):
            self._write('<code>')
            self._write(_escape_html(ev.text))
            self._write('</code>')
        elif isinstance(ev, (Html, InlineHtml)):
            self._write(ev.text)
        elif isinstance(ev, SoftBreak):
            self._write('\n')
        elif isinstance(ev, HardBreak):
            self._write('<br />\n')
        elif isinstance(ev, Rule):
            self._newline()
            self._write('<hr />\n')
        elif isinstance(ev, TaskListMarker):
            if ev.checked:
                self._write('<input disabled="" type="checkbox" checked=""/>\n')
            else:
                self._write('<input disabled="" type="checkbox"/>\n')
        else:
            raise TypeError(ev)

    # image alt collection

    def _open_image(self, tag: Image) -> None:
        self._image_nesting += 1
        self._image_dest_url.append(tag.dest_url)
        self._image_title.append(tag.title)
        self._image_alt_buf.append([])

    def _absorb_into_alt(self, ev: Event) -> None:
        # Only text-bearing events contribute. We intentionally drop SoftBreak / HardBreak HTML markup and substitute
        # plain spaces / newlines instead.
        buf = self._image_alt_buf[-1]
        if isinstance(ev, Text):
            buf.append(ev.text)
        elif isinstance(ev, Code):
            buf.append(ev.text)
        elif isinstance(ev, (Html, InlineHtml)):
            # CM spec says inline HTML inside image alt becomes plain text; we don't strip tags (the spec test 494 shows
            # simple cases work as-is once stripped of nested image rendering, but we do flatten). For our purposes,
            # write the raw HTML chars; the alt attribute will be HTML-escaped by the caller.
            buf.append(ev.text)
        elif isinstance(ev, SoftBreak):
            buf.append('\n')
        elif isinstance(ev, HardBreak):
            buf.append('\n')

    def _close_image(self) -> None:
        dest = self._image_dest_url.pop()
        title = self._image_title.pop()
        alt_parts = self._image_alt_buf.pop()
        self._image_nesting -= 1
        alt = ''.join(alt_parts)
        if self._image_nesting > 0:
            # Nested image: contributes its alt text to the outer image's buffer.
            self._image_alt_buf[-1].append(alt)
            return
        # Emit the <img> tag.
        self._write(f'<img src="{_escape_href(dest)}" alt="{_escape_html(alt)}"')
        if title:
            self._write(f' title="{_escape_html(title)}"')
        self._write(' />')

    #

    def _start_tag(self, tag) -> None:
        if isinstance(tag, Paragraph):
            self._newline()
            self._write('<p>')
        elif isinstance(tag, Heading):
            self._newline()
            self._write(f'<h{tag.level}>')
        elif isinstance(tag, BlockQuote):
            self._newline()
            if tag.kind is not None:
                # GFM admonition: class attr on the blockquote.
                self._write(f'<blockquote class="markdown-alert-{tag.kind.value}">\n')
            else:
                self._write('<blockquote>\n')
        elif isinstance(tag, FencedCodeBlock):
            self._newline()
            if tag.info:
                # Take only the first word of the info string as language class.
                lang = tag.info.split(None, 1)[0]
                self._write(f'<pre><code class="language-{_escape_html(lang)}">')
            else:
                self._write('<pre><code>')
        elif isinstance(tag, IndentedCodeBlock):
            self._newline()
            self._write('<pre><code>')
        elif isinstance(tag, HtmlBlock):
            # No wrapper — content is raw HTML emitted via Html events.
            pass
        elif isinstance(tag, List):
            self._newline()
            if tag.start is None:
                self._write('<ul>\n')
            elif tag.start == 1:
                self._write('<ol>\n')
            else:
                self._write(f'<ol start="{tag.start}">\n')
        elif isinstance(tag, Item):
            self._newline()
            self._write('<li>')
        elif isinstance(tag, Table):
            self._newline()
            self._write('<table>')
            self._newline()
            self._table_alignments.append(tuple(tag.alignments))
            self._table_in_head.append(False)
            self._table_cell_ix.append(0)
            self._table_body_open.append(False)
        elif isinstance(tag, TableHead):
            self._table_in_head[-1] = True
            self._table_cell_ix[-1] = 0
            self._write('<thead>')
            self._newline()
            self._write('<tr>')
            self._newline()
        elif isinstance(tag, TableRow):
            self._table_cell_ix[-1] = 0
            if not self._table_body_open[-1]:
                self._write('<tbody>')
                self._newline()
                self._table_body_open[-1] = True
            self._write('<tr>')
            self._newline()
        elif isinstance(tag, TableCell):
            cell_ix = self._table_cell_ix[-1]
            aligns = self._table_alignments[-1]
            align = aligns[cell_ix] if cell_ix < len(aligns) else Alignment.NONE
            tag_name = 'th' if self._table_in_head[-1] else 'td'
            align_attr = _align_attr(align)
            self._write(f'<{tag_name}{align_attr}>')
            self._table_cell_ix[-1] = cell_ix + 1
        elif isinstance(tag, Emphasis):
            self._write('<em>')
        elif isinstance(tag, Strong):
            self._write('<strong>')
        elif isinstance(tag, Strikethrough):
            self._write('<del>')
        elif isinstance(tag, Link):
            href = _escape_href(tag.dest_url)
            self._write(f'<a href="{href}"')
            if tag.title:
                self._write(f' title="{_escape_html(tag.title)}"')
            self._write('>')
        # Image starts are handled by _dispatch via _open_image — they switch the renderer into alt-text-collection mode
        # and never reach _start_tag.
        else:
            raise TypeError(tag)

    def _end_tag(self, tag) -> None:
        if isinstance(tag, Paragraph):
            self._write('</p>\n')
        elif isinstance(tag, Heading):
            self._write(f'</h{tag.level}>\n')
        elif isinstance(tag, BlockQuote):
            self._newline()
            self._write('</blockquote>\n')
        elif isinstance(tag, (FencedCodeBlock, IndentedCodeBlock)):
            self._write('</code></pre>\n')
        elif isinstance(tag, HtmlBlock):
            pass
        elif isinstance(tag, List):
            self._newline()
            self._write('</ul>\n' if tag.start is None else '</ol>\n')
        elif isinstance(tag, Item):
            self._write('</li>\n')
        elif isinstance(tag, Table):
            if self._table_body_open[-1]:
                self._write('</tbody>')
                self._newline()
            else:
                # No body rows — emit empty <tbody></tbody> (pulldown / GFM convention).
                self._write('<tbody></tbody>')
                self._newline()
            self._write('</table>')
            self._newline()
            self._table_alignments.pop()
            self._table_in_head.pop()
            self._table_cell_ix.pop()
            self._table_body_open.pop()
        elif isinstance(tag, TableHead):
            self._write('</tr>')
            self._newline()
            self._write('</thead>')
            self._newline()
            self._table_in_head[-1] = False
        elif isinstance(tag, TableRow):
            self._write('</tr>')
            self._newline()
        elif isinstance(tag, TableCell):
            tag_name = 'th' if self._table_in_head[-1] else 'td'
            self._write(f'</{tag_name}>')
            self._newline()
        elif isinstance(tag, Emphasis):
            self._write('</em>')
        elif isinstance(tag, Strong):
            self._write('</strong>')
        elif isinstance(tag, Strikethrough):
            self._write('</del>')
        elif isinstance(tag, Link):
            self._write('</a>')
        # Image ends are handled by _dispatch via _close_image.
        else:
            raise TypeError(tag)
