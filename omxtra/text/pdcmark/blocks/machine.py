"""
Line-driven block parser state machine.

Closest pulldown-cmark analogue: `pulldown-cmark/src/firstpass.rs::FirstPass`. Same line-driven model, same per-line
container-continuation / new-container / new-leaf / content phases, but exposed via a public `feed_line` entry rather
than driven by a single internal `run()` loop, and emitting events directly instead of building a `Tree<Item>`.

Algorithm sketch for `feed_line`:

  1. Walk the open container stack matching continuation markers. Track `matched_depth` — the
     number of containers that continued. (See `_walk_continuations`; mirrors
     pulldown-cmark/src/parse.rs::scan_containers.)
  2. Decide how to handle unmatched containers:
     - Paragraph + non-blank, non-new-block remainder ⇒ lazy continuation: leave the stack alone, treat the whole line
       as paragraph content.
     - Otherwise: close unmatched containers (and any open leaf in them).
  3. Try to open new containers in a loop (blockquote `>`, list marker). A list marker may
     reuse an existing same-type list rather than open a fresh one.
  4. Dispatch the remaining line content to leaf-block recognition (ATX heading, hrule, fence,
     HTML block, indented code, paragraph).
"""
from omlish import dataclasses as dc

from ..events import BlockQuote
from ..events import BlockQuoteKind
from ..events import End
from ..events import Event
from ..events import FencedCodeBlock
from ..events import Heading
from ..events import Html
from ..events import HtmlBlock
from ..events import IndentedCodeBlock
from ..events import Item
from ..events import List
from ..events import Paragraph
from ..events import Rule
from ..events import Start
from ..events import Table
from ..events import TableCell
from ..events import TableHead
from ..events import TableRow
from ..events import TaskListMarker
from ..events import Text
from ..inlines.links import Fuel
from ..inlines.parser import InlineParser
from ..options import Options
from ..scanning.atx import scan_atx_open
from ..scanning.blockquotes import scan_blockquote_marker
from ..scanning.fences import is_fence_close
from ..scanning.fences import scan_fence_open
from ..scanning.hrule import scan_hrule
from ..scanning.htmlblocks import html_block_close_on_line
from ..scanning.htmlblocks import html_block_closes_on_blank_line
from ..scanning.htmlblocks import scan_html_block_start
from ..scanning.lines import LineStart
from ..scanning.lists import scan_list_marker
from ..scanning.lists import scan_task_list_marker
from ..scanning.setext import scan_setext_underline
from ..scanning.tables import count_table_cells as _count_table_cells
from ..scanning.tables import line_could_be_table_row
from ..scanning.tables import parse_alignment_row
from ..scanning.tables import parse_table_row
from ..scanning.whitespace import is_blank_line
from .containers import OpenBlockQuote
from .containers import OpenContainer
from .containers import OpenItem
from .containers import OpenList
from .leaves import BufferedLine
from .leaves import OpenFencedCode
from .leaves import OpenHtmlBlock
from .leaves import OpenIndentedCode
from .leaves import OpenLeaf
from .leaves import OpenParagraph
from .leaves import OpenTable
from .refdefs import RefDefs
from .refdefs import try_consume_refdef


##


def _strip_columns(line: str, columns: int) -> str:
    """Remove up to `columns` columns of leading whitespace, respecting tab-stops at 4."""

    cols = 0
    i = 0
    n = len(line)
    while i < n and cols < columns:
        c = line[i]
        if c == ' ':
            cols += 1
            i += 1
        elif c == '\t':
            advance = 4 - (cols % 4)
            if cols + advance <= columns:
                cols += advance
                i += 1
            else:
                spaces = cols + advance - columns
                return ' ' * spaces + line[i + 1:]
        else:
            break
    return line[i:]


def _post_marker_indent(line: str, marker_end: int) -> int:
    """
    Compute the column count for content following a list marker, per CommonMark §5.2:

      - blank line after marker → default 1 column,
      - 1-4 spaces / equivalent tabs → that many columns,
      - 5+ spaces → only 1 column (extras become indented-code within the item),

    The returned value is the post-marker indent in logical columns.
    """

    if marker_end >= len(line) or is_blank_line(line[marker_end:]):
        return 1
    cols = 0
    i = marker_end
    n = len(line)
    while i < n and cols < 5:
        c = line[i]
        if c == ' ':
            cols += 1
            i += 1
        elif c == '\t':
            cols += 4 - (cols % 4)
            i += 1
        else:
            break
    if cols == 0 or cols > 4:
        return 1
    return cols


##


# pulldown-cmark/src/firstpass.rs::FirstPass — same line-driven model exposed as feed_line(); emits events directly
# instead of building a Tree<Item>.
class BlockMachine:
    def __init__(
            self,
            options: Options,
            *,
            refdefs: RefDefs | None = None,
    ) -> None:
        super().__init__()

        self._options = options
        self._refdefs = refdefs if refdefs is not None else RefDefs()
        # Share refdefs + fuel with the inline parser so refdefs collected during block parsing become visible to inline
        # link resolution and vice versa.
        self._fuel = Fuel(remaining=options.link_ref_expansion_min)
        self._inline = InlineParser(options, refdefs=self._refdefs, fuel=self._fuel)
        self._stack: list[OpenContainer] = []
        self._open: OpenLeaf | None = None
        self._terminated = False

    @property
    def refdefs(self) -> RefDefs:
        return self._refdefs

    @property
    def has_open_block(self) -> bool:
        return self._open is not None or bool(self._stack)

    # Public entry points.

    def feed_line(self, line: str, line_start: int, line_next: int) -> list[Event]:
        if self._terminated:
            raise RuntimeError('BlockMachine: feed_line after finish()')
        bl = BufferedLine(text=line, line_start=line_start, line_next=line_next)
        events: list[Event] = []
        self._process_line(bl, events)
        return events

    def tentative_events(self, fallback_next: int) -> list[Event]:
        """Events that would emit right now if input ended without further `feed_line`s. Does NOT mutate state."""

        if self._open is None and not self._stack:
            return []
        events: list[Event] = []
        if self._open is not None:
            events.extend(self._close_to_events(self._open, fallback_next))
        for c in reversed(self._stack):
            events.append(self._close_container_event(c, fallback_next))
        return events

    def finish(self, final_offset: int) -> list[Event]:
        if self._terminated:
            return []
        events: list[Event] = []
        if self._open is not None:
            events.extend(self._close_to_events(self._open, final_offset))
            self._open = None
        while self._stack:
            events.append(self._close_container_event(self._stack.pop(), final_offset))
        self._terminated = True
        return events

    # Per-line dispatch.

    def _process_line(self, bl: BufferedLine, events: list[Event]) -> None:
        ls = LineStart(bl.text)
        matched_depth = self._walk_continuations(ls)
        blank = is_blank_line(ls.remaining())

        # Lazy continuation: an open paragraph absorbs the line even if some outer containers' markers were missed. We
        # require the line not to be blank AND not to be a new-block starter at the *post-container-walk* position.
        # `ls.remaining()` is what's left after the matched containers' marker / indent consumption — that's the
        # context against which "is this a new block?" should be evaluated, NOT the raw line (whose leading whitespace
        # belongs to the unmatched outer containers).
        if (
            matched_depth < len(self._stack)
            and isinstance(self._open, OpenParagraph)
            and not blank
            and not self._line_starts_new_block(ls.remaining())
        ):
            self._open = dc.replace(self._open, lines=(*self._open.lines, bl))
            return

        # Lists themselves have no continuation marker; they continue iff a same-type item starts here or some inner
        # container did. If the deepest matched container is a List and the line doesn't open a same-type marker, the
        # List itself also closes. (Blank lines do not trigger List closure — a single blank between items only marks
        # the list "loose".)
        if not blank:
            while (
                matched_depth > 0
                and isinstance(self._stack[matched_depth - 1], OpenList)
                and not self._line_opens_matching_item(self._stack[matched_depth - 1], ls)
            ):
                matched_depth -= 1

        if matched_depth < len(self._stack):
            self._close_to_depth(matched_depth, events, bl.line_start)

        # Open new containers in a loop. Each iteration may push one container.
        while True:
            ls_save = ls.clone()
            if self._try_open_new_container(ls, bl, events):
                continue
            ls.restore(ls_save)
            break

        # Process the remaining line content. Re-check blankness here — container openers (e.g. GFM `> [!NOTE]`) may
        # have consumed the entire post-marker remainder of the line.
        if blank or is_blank_line(ls.remaining()):
            self._handle_blank(bl, events)
            return

        # This line is non-blank content. Any open list whose `had_blank` flag is set just had content arrive after a
        # blank → the list is loose.
        self._reconcile_list_loose_on_content()

        self._dispatch_leaf(bl, ls, events)

    def _reconcile_list_loose_on_content(self) -> None:
        for i, c in enumerate(self._stack):
            if isinstance(c, OpenList) and c.had_blank:
                self._stack[i] = dc.replace(c, had_blank=False, is_loose=True)

    def _line_opens_matching_item(self, lst: OpenList, ls: LineStart) -> bool:
        """
        Peek (without consuming) at the line under `ls` to see if a list marker of the same type as `lst` starts here
        (after up-to-3-space indent).
        """

        save = ls.clone()
        leading = ls.scan_space_upto(3)
        if leading == 3 and ls.position < len(ls.line) and ls.line[ls.position] == ' ':
            ls.restore(save)
            return False
        rem = ls.remaining()
        ls.restore(save)
        marker = scan_list_marker(rem)
        if marker is None:
            return False
        if marker.is_ordered != lst.is_ordered:
            return False
        if marker.char != lst.marker_char:
            return False
        # An hrule like `- - -` wins; don't reuse the list in that case.
        if not marker.is_ordered and marker.char in '-*' and scan_hrule(rem):
            return False
        return True

    # Container stack walk.

    def _walk_continuations(self, ls: LineStart) -> int:
        # pulldown-cmark/src/parse.rs::scan_containers — same per-container check set.
        matched = 0
        for c in self._stack:
            if isinstance(c, OpenBlockQuote):
                save = ls.clone()
                ls.scan_space_upto(3)
                if scan_blockquote_marker(ls.remaining()) is None:
                    ls.restore(save)
                    break
                ls.scan_ch('>')
                if ls.position < len(ls.line) and ls.line[ls.position] in ' \t':
                    ls.scan_space(1)
            elif isinstance(c, OpenList):
                # Lists themselves have no marker; their inner items carry the indent requirement. Always "matches"
                # here, mirroring scan_containers' fallthrough.
                pass
            elif isinstance(c, OpenItem):
                save = ls.clone()
                if not ls.scan_space(c.content_indent) and not ls.is_at_eol():
                    ls.restore(save)
                    break
            matched += 1
        return matched

    def _close_to_depth(self, depth: int, events: list[Event], line_offset: int) -> None:
        # First close any open leaf — it belongs to the innermost (currently doomed) container.
        if self._open is not None:
            events.extend(self._close_to_events(self._open, line_offset))
            self._open = None
        while len(self._stack) > depth:
            events.append(self._close_container_event(self._stack.pop(), line_offset))

    # New-container opening.

    def _try_open_new_container(self, ls: LineStart, bl: BufferedLine, events: list[Event]) -> bool:
        # Up-to-3-space indent then the marker. 4+ columns means the line is indented-code or paragraph content; no
        # container can start there.
        save = ls.clone()
        leading = ls.scan_space_upto(3)
        if leading == 3 and ls.position < len(ls.line) and ls.line[ls.position] == ' ':
            # Actually 4+ spaces of indent — no container start here.
            ls.restore(save)
            return False

        # Blockquote marker.
        rem = ls.remaining()
        bq = scan_blockquote_marker(rem)
        if bq is not None:
            # An open leaf at this level is a paragraph being interrupted (or a code/html block that's about to be
            # displaced). Close it before nesting deeper.
            if self._open is not None:
                events.extend(self._close_to_events(self._open, bl.line_start))
                self._open = None
            # Consume the marker.
            ls.scan_ch('>')
            if ls.position < len(ls.line) and ls.line[ls.position] in ' \t':
                ls.scan_space(1)
            # GFM admonition tag: `[!NOTE]` / `[!TIP]` / ... on the first content line. Consumed entirely; the next line
            # begins the actual blockquote content.
            kind: BlockQuoteKind | None = None
            if self._options.gfm_blockquote_kinds:
                kind = _scan_blockquote_kind_consuming(ls)
            events.append(Start(
                offset=(bl.line_start + ls.position, bl.line_next),
                tag=BlockQuote(kind=kind),
            ))
            self._stack.append(OpenBlockQuote(
                open_start=bl.line_start + ls.position,
                kind=kind,
            ))
            return True

        # List marker. Bullet markers `-` and `*` lose to thematic breaks on the same line (`- - -` is hrule, not a
        # list). Cf. pulldown-cmark/src/scanners.rs::scan_hrule and the priority dance in
        # LineStart::scan_list_marker_with_indent.
        marker = scan_list_marker(rem)
        if marker is not None and not marker.is_ordered and marker.char in '-*' and scan_hrule(rem):
            ls.restore(save)
            return False
        if marker is not None:
            # Only marker `1.` / `1)` may interrupt a paragraph (CommonMark §5.2 example 277-279). ATX-ish interrupters
            # and other block starters already handled in lazy-continuation check; for list markers we apply the
            # additional CM constraint that ordered lists interrupting a paragraph must have start=1.
            if isinstance(self._open, OpenParagraph) and marker.is_ordered and marker.start != 1:
                ls.restore(save)
                return False

            # Determine if this list-marker continues an existing same-type list.
            existing_list: OpenList | None = (
                self._stack[-1] if self._stack and isinstance(self._stack[-1], OpenList) else None
            )
            if existing_list is not None and (
                existing_list.is_ordered != marker.is_ordered
                or existing_list.marker_char != marker.char
            ):
                # Different list kind — close it first.
                if self._open is not None:
                    events.extend(self._close_to_events(self._open, bl.line_start))
                    self._open = None
                events.append(self._close_container_event(self._stack.pop(), bl.line_start))
                existing_list = None

            marker_start_in_line = ls.position
            # Consume the marker characters themselves.
            for _ in range(marker.marker_width):
                ls.scan_ch(ls.line[ls.position])
            marker_end_in_line = ls.position
            post_indent = _post_marker_indent(ls.line, marker_end_in_line)
            content_indent = leading + marker.marker_width + post_indent

            # Close any open leaf at this level before opening the new list / item.
            if self._open is not None:
                events.extend(self._close_to_events(self._open, bl.line_start))
                self._open = None
            if existing_list is None:
                events.append(Start(
                    offset=(bl.line_start + marker_start_in_line, bl.line_next),
                    tag=List(
                        start=marker.start if marker.is_ordered else None,
                    ),
                ))
                self._stack.append(OpenList(
                    is_ordered=marker.is_ordered,
                    marker_char=marker.char,
                    start=marker.start,
                    open_start=bl.line_start + marker_start_in_line,
                ))
            else:
                # Close previous item.
                while self._stack and isinstance(self._stack[-1], OpenItem):
                    events.append(self._close_container_event(self._stack.pop(), bl.line_start))

            events.append(Start(
                offset=(bl.line_start + marker_start_in_line, bl.line_next),
                tag=Item(),
            ))
            self._stack.append(OpenItem(
                content_indent=content_indent,
                open_start=bl.line_start + marker_start_in_line,
                open_next=bl.line_next,
            ))

            # Consume the post-marker indent from the LineStart cursor.
            ls.scan_space(post_indent)

            # GFM task list marker: scan immediately after the post-marker indent. Only emitted if the option is on.
            if self._options.tasklists:
                tl = scan_task_list_marker(ls.remaining())
                if tl is not None:
                    abs_start = bl.line_start + ls.position
                    abs_end = bl.line_start + ls.position + tl.end
                    events.append(TaskListMarker(
                        offset=(abs_start, abs_end),
                        checked=tl.checked,
                    ))
                    ls.advance(tl.end)
                    if ls.position < len(ls.line) and ls.line[ls.position] == ' ':
                        ls.scan_space(1)
            return True

        ls.restore(save)
        return False

    # Leaf dispatch.

    def _dispatch_leaf(self, bl: BufferedLine, ls: LineStart, events: list[Event]) -> None:
        # Now operate on the content after consumed container markers.
        content_offset_in_line = ls.position
        content = ls.remaining()
        absolute_content_start = bl.line_start + content_offset_in_line

        # If a leaf is already open, dispatch to its per-type continuation handler.
        if self._open is not None:
            open_ = self._open
            if isinstance(open_, OpenFencedCode):
                self._feed_fenced_code(open_, bl, content, absolute_content_start, events)
                return
            if isinstance(open_, OpenHtmlBlock):
                self._feed_html_block(open_, bl, content, absolute_content_start, events)
                return
            if isinstance(open_, OpenTable):
                self._feed_table(open_, bl, ls, content, absolute_content_start, events)
                return
            if isinstance(open_, OpenIndentedCode):
                # Continuation requires 4+ columns of indent relative to the container; we
                # already consumed container markers so we measure on `content`.
                if _leading_indent(content) >= 4 or is_blank_line(content):
                    new_line = dc.replace(
                        bl,
                        text=_strip_columns(content, 4),
                        line_start=absolute_content_start,
                    )
                    self._open = dc.replace(open_, lines=(*open_.lines, new_line))
                    return
                events.extend(self._close_to_events(open_, bl.line_start))
                self._open = None
                # Fall through to fresh leaf opening on the same line.
            elif isinstance(open_, OpenParagraph):
                # Setext underline?
                if _leading_indent(content) < 4:
                    setext_level = scan_setext_underline(content)
                else:
                    setext_level = None
                if setext_level is not None:
                    self._emit_paragraph_or_heading(
                        open_, bl.line_next, events, heading_level=setext_level,
                    )
                    self._open = None
                    return
                # Table head promotion — the LAST line of the open paragraph is a header candidate iff it contains a
                # `|`. The line under inspection (`content`) is the alignment row. Per GFM, the head row's column count
                # must match the alignment row's exactly; padding doesn't count.
                if (
                    self._options.tables
                    and line_could_be_table_row(open_.lines[-1].text)
                ):
                    align = parse_alignment_row(content)
                    if align is not None:
                        head_line = open_.lines[-1]
                        head_count = _count_table_cells(head_line.text)
                        if head_count == len(align):
                            head_cells = parse_table_row(head_line.text, len(align))
                            # Emit any preceding paragraph lines as a separate paragraph.
                            if len(open_.lines) > 1:
                                preceding = OpenParagraph(lines=open_.lines[:-1])
                                self._emit_paragraph_or_heading(
                                    preceding,
                                    head_line.line_start,
                                    events,
                                    heading_level=None,
                                )
                            self._emit_table_open(head_line, bl.line_next, align, head_cells, events)
                            self._open = OpenTable(
                                alignments=align,
                                open_start=head_line.line_start,
                            )
                            return
                if self._line_starts_new_block(content):
                    events.extend(self._close_to_events(open_, bl.line_start))
                    self._open = None
                    # Fall through to fresh leaf opening.
                else:
                    # Direct paragraph continuation (we already consumed container markers).
                    new_bl = dc.replace(bl, text=content, line_start=absolute_content_start)
                    self._open = dc.replace(open_, lines=(*open_.lines, new_bl))
                    return

        # No open leaf (or it just closed): try to open one.
        self._open_fresh(bl, content, absolute_content_start, events)

    def _open_fresh(
            self,
            bl: BufferedLine,
            content: str,
            absolute_content_start: int,
            events: list[Event],
    ) -> None:
        # Indented code block (only when no other context applies).
        if _leading_indent(content) >= 4:
            stripped = _strip_columns(content, 4)
            self._open = OpenIndentedCode(lines=(dc.replace(
                bl,
                text=stripped,
                line_start=absolute_content_start,
            ),))
            return

        # Strip up to 3 leading spaces for the dispatchers below.
        i = 0
        while i < len(content) and content[i] == ' ' and i < 3:
            i += 1
        body = content[i:]
        body_offset = absolute_content_start + i

        # ATX heading.
        atx = scan_atx_open(body)
        if atx is not None:
            level = atx.level
            content_text = body[atx.content_start:atx.content_end]
            events.append(Start(
                offset=(absolute_content_start, bl.line_next),
                tag=Heading(level=level),
            ))
            if content_text:
                inline_bl = BufferedLine(
                    text=content_text,
                    line_start=body_offset + atx.content_start,
                    line_next=body_offset + atx.content_end,
                )
                events.extend(self._inline.parse((inline_bl,)))
            events.append(End(
                offset=(absolute_content_start, bl.line_next),
                tag=Heading(level=level),
            ))
            return

        # Thematic break.
        if scan_hrule(body):
            events.append(Rule(offset=(absolute_content_start, bl.line_next)))
            return

        # Fenced code open.
        fence = scan_fence_open(body)
        if fence is not None:
            self._open = OpenFencedCode(
                fence_char=fence.fence_char,
                fence_length=fence.fence_length,
                fence_indent=i,
                info=fence.info,
                open_start=absolute_content_start,
                open_next=bl.line_next,
                content=(),
            )
            return

        # HTML block start.
        html_start = scan_html_block_start(body)
        if html_start is not None:
            block = OpenHtmlBlock(
                html_type=html_start.type,
                open_start=absolute_content_start,
                lines=(dc.replace(bl, text=content, line_start=absolute_content_start),),
            )
            if (
                not html_block_closes_on_blank_line(block.html_type)
                and html_block_close_on_line(block.html_type, body)
            ):
                events.extend(self._close_to_events(block, bl.line_next))
                return
            self._open = block
            return

        # Default — open a paragraph.
        new_bl = dc.replace(bl, text=content, line_start=absolute_content_start)
        self._open = OpenParagraph(lines=(new_bl,))

    # Leaf-block feed helpers.

    def _feed_fenced_code(
            self,
            open_: OpenFencedCode,
            bl: BufferedLine,
            content: str,
            absolute_content_start: int,
            events: list[Event],
    ) -> None:
        # The fence's leading-indent count is stripped from each content line first.
        stripped = _strip_columns(content, open_.fence_indent)
        if is_fence_close(stripped, open_.fence_char, open_.fence_length):
            events.extend(self._close_to_events(open_, bl.line_next))
            self._open = None
            return
        new_line = BufferedLine(
            text=stripped,
            line_start=absolute_content_start,
            line_next=bl.line_next,
        )
        self._open = dc.replace(open_, content=(*open_.content, new_line))

    def _emit_table_open(
            self,
            head_line: BufferedLine,
            head_end_offset: int,
            alignments: tuple,
            head_cells: list[str],
            events: list[Event],
    ) -> None:
        events.append(Start(
            offset=(head_line.line_start, head_end_offset),
            tag=Table(alignments=alignments),
        ))
        events.append(Start(
            offset=(head_line.line_start, head_line.line_next),
            tag=TableHead(),
        ))
        self._emit_table_cells(head_line, head_cells, events)
        events.append(End(
            offset=(head_line.line_start, head_line.line_next),
            tag=TableHead(),
        ))

    def _emit_table_cells(
            self,
            row_line: BufferedLine,
            cells: list[str],
            events: list[Event],
    ) -> None:
        for cell_text in cells:
            events.append(Start(
                offset=(row_line.line_start, row_line.line_next),
                tag=TableCell(),
            ))
            if cell_text:
                # Inline-parse the cell content. We give it a synthetic single-line wrap; offsets are approximate (the
                # per-cell source-offset accounting would require tracking each cell's start position back into the row
                # line, which is doable but adds noise to the table scanner — punted to a later refinement).
                synth = BufferedLine(
                    text=cell_text,
                    line_start=row_line.line_start,
                    line_next=row_line.line_next,
                )
                events.extend(self._inline.parse((synth,)))
            events.append(End(
                offset=(row_line.line_start, row_line.line_next),
                tag=TableCell(),
            ))

    def _feed_table(
            self,
            open_: OpenTable,
            bl: BufferedLine,
            ls: LineStart,
            content: str,
            absolute_content_start: int,
            events: list[Event],
    ) -> None:
        # A blank line ALWAYS ends the table. Other non-row content (any line that doesn't contain at least one `|`, but
        # per GFM a single-column row is allowed with no pipe at all if the table is open with single-column alignments)
        # — we accept anything non-blank while the table is open, treating it as a row.
        if is_blank_line(content):
            events.extend(self._close_to_events(open_, bl.line_start))
            self._open = None
            self._dispatch_leaf(bl, ls, events)
            return
        # Any leaf-level construct (atx heading, fenced code, etc.) also terminates the table.
        if self._line_starts_new_block(content):
            events.extend(self._close_to_events(open_, bl.line_start))
            self._open = None
            self._dispatch_leaf(bl, ls, events)
            return
        cells = parse_table_row(content, len(open_.alignments))
        row_line = BufferedLine(
            text=content,
            line_start=absolute_content_start,
            line_next=bl.line_next,
        )
        events.append(Start(
            offset=(row_line.line_start, row_line.line_next),
            tag=TableRow(),
        ))
        self._emit_table_cells(row_line, cells, events)
        events.append(End(
            offset=(row_line.line_start, row_line.line_next),
            tag=TableRow(),
        ))

    def _feed_html_block(
            self,
            open_: OpenHtmlBlock,
            bl: BufferedLine,
            content: str,
            absolute_content_start: int,
            events: list[Event],
    ) -> None:
        if html_block_closes_on_blank_line(open_.html_type) and is_blank_line(content):
            events.extend(self._close_to_events(open_, bl.line_start))
            self._open = None
            return
        new_line = BufferedLine(
            text=content,
            line_start=absolute_content_start,
            line_next=bl.line_next,
        )
        new_block = dc.replace(open_, lines=(*open_.lines, new_line))
        if (
            not html_block_closes_on_blank_line(open_.html_type)
            and html_block_close_on_line(open_.html_type, content)
        ):
            events.extend(self._close_to_events(new_block, bl.line_next))
            self._open = None
            return
        self._open = new_block

    # Blank-line and "is this a new block?" helpers.

    def _handle_blank(self, bl: BufferedLine, events: list[Event]) -> None:
        # Tight / loose: record on every open list. If non-blank content later arrives still inside the list, the list
        # flips to loose; if the list closes without further content, the trailing blank doesn't make it loose.
        for i, c in enumerate(self._stack):
            if isinstance(c, OpenList) and not c.had_blank:
                self._stack[i] = dc.replace(c, had_blank=True)
        # Close an open paragraph or indented-code block; fenced-code and html blocks 1-5 stay.
        if isinstance(self._open, OpenParagraph):
            events.extend(self._close_to_events(self._open, bl.line_start))
            self._open = None
            return
        if isinstance(self._open, OpenIndentedCode):
            # Blank lines inside indented code are kept (with empty text); on close they're stripped by
            # `_emit_indented_code`.
            new_line = BufferedLine(text='', line_start=bl.line_start, line_next=bl.line_next)
            self._open = dc.replace(self._open, lines=(*self._open.lines, new_line))
            return
        if isinstance(self._open, OpenFencedCode):
            # Blank lines inside a fenced code block are content.
            new_line = BufferedLine(text='', line_start=bl.line_start, line_next=bl.line_next)
            self._open = dc.replace(self._open, content=(*self._open.content, new_line))
            return
        if isinstance(self._open, OpenHtmlBlock):
            if html_block_closes_on_blank_line(self._open.html_type):
                events.extend(self._close_to_events(self._open, bl.line_start))
                self._open = None
                return
            new_line = BufferedLine(text='', line_start=bl.line_start, line_next=bl.line_next)
            self._open = dc.replace(self._open, lines=(*self._open.lines, new_line))
            return
        # No open leaf — blank lines just pass through.

    def _line_starts_new_block(self, line: str) -> bool:
        """
        True if `line` starts a new block construct that would *interrupt* an open paragraph. Used to decide whether
        lazy / direct paragraph continuation applies.

        The CommonMark "ordered list with start != 1 cannot interrupt a paragraph" rule only applies when there is no
        enclosing list of matching type — a `2.` on a line whose enclosing list is ordered-with-period continues that
        list and therefore interrupts the prior item's paragraph.
        """

        if _leading_indent(line) >= 4:
            return False
        i = 0
        while i < len(line) and line[i] == ' ' and i < 3:
            i += 1
        body = line[i:]
        if scan_atx_open(body) is not None:
            return True
        if scan_hrule(body):
            return True
        if scan_fence_open(body) is not None:
            return True
        html_start = scan_html_block_start(body)
        if html_start is not None and html_start.can_interrupt_paragraph:
            return True
        if scan_blockquote_marker(body) is not None:
            return True
        marker = scan_list_marker(body)
        if marker is not None:
            # Bullet `-` / `*` only — `- - -` is a thematic break, not a list-marker interrupt.
            if not marker.is_ordered and marker.char in '-*' and scan_hrule(body):
                return False
            if marker.is_ordered and marker.start != 1:
                # Only interrupts if some enclosing list has matching type.
                for c in self._stack:
                    if (
                        isinstance(c, OpenList)
                        and c.is_ordered == marker.is_ordered
                        and c.marker_char == marker.char
                    ):
                        return True
                return False
            return True
        return False

    # Close-and-emit.

    def _close_to_events(self, open_: OpenLeaf, end_offset: int) -> list[Event]:
        if isinstance(open_, OpenParagraph):
            return self._emit_paragraph_or_heading(open_, end_offset, heading_level=None)
        if isinstance(open_, OpenFencedCode):
            return self._emit_fenced_code(open_, end_offset)
        if isinstance(open_, OpenIndentedCode):
            return self._emit_indented_code(open_, end_offset)
        if isinstance(open_, OpenHtmlBlock):
            return self._emit_html_block(open_, end_offset)
        if isinstance(open_, OpenTable):
            return [End(offset=(open_.open_start, end_offset), tag=Table(alignments=open_.alignments))]
        raise TypeError(open_)

    def _emit_paragraph_or_heading(
            self,
            p: OpenParagraph,
            end_offset: int,
            events: list[Event] | None = None,
            *,
            heading_level: int | None,
    ) -> list[Event]:
        out: list[Event] = events if events is not None else []
        # Refdef peel — only for plain paragraphs (a setext-promoted heading uses the entire paragraph as heading
        # content, so refdefs would be inside the heading text per CM).
        lines = p.lines
        if heading_level is None:
            lines = self._consume_leading_refdefs(lines)
            if not lines:
                return out  # entire paragraph was refdefs; emit nothing
        first = lines[0]
        tag: Paragraph | Heading = (
            Paragraph() if heading_level is None else Heading(level=heading_level)
        )
        out.append(Start(offset=(first.line_start, end_offset), tag=tag))
        out.extend(self._inline.parse(lines))
        out.append(End(offset=(first.line_start, end_offset), tag=tag))
        return out

    def _consume_leading_refdefs(
            self,
            lines: tuple[BufferedLine, ...],
    ) -> tuple[BufferedLine, ...]:
        texts = [ln.text for ln in lines]
        i = 0
        while i < len(lines):
            match = try_consume_refdef(texts, i)
            if match is None:
                break
            self._refdefs.add(match.label, match.link_def)
            i += match.lines_consumed
        return lines[i:]

    def _emit_fenced_code(self, c: OpenFencedCode, end_offset: int) -> list[Event]:
        out: list[Event] = []
        tag = FencedCodeBlock(info=c.info)
        out.append(Start(offset=(c.open_start, end_offset), tag=tag))
        for bl in c.content:
            out.append(Text(
                offset=(bl.line_start, bl.line_next),
                text=bl.text + '\n',
            ))
        out.append(End(offset=(c.open_start, end_offset), tag=tag))
        return out

    def _emit_indented_code(self, c: OpenIndentedCode, end_offset: int) -> list[Event]:
        lines = list(c.lines)
        while lines and is_blank_line(lines[-1].text):
            lines.pop()
        if not lines:
            return []
        first = lines[0]
        last_next = lines[-1].line_next
        out: list[Event] = []
        tag = IndentedCodeBlock()
        out.append(Start(offset=(first.line_start, last_next), tag=tag))
        for bl in lines:
            out.append(Text(
                offset=(bl.line_start, bl.line_next),
                text=bl.text + '\n',
            ))
        out.append(End(offset=(first.line_start, last_next), tag=tag))
        return out

    def _emit_html_block(self, h: OpenHtmlBlock, end_offset: int) -> list[Event]:
        out: list[Event] = []
        tag = HtmlBlock()
        first = h.lines[0]
        out.append(Start(offset=(first.line_start, end_offset), tag=tag))
        for bl in h.lines:
            out.append(Html(
                offset=(bl.line_start, bl.line_next),
                text=bl.text + '\n',
            ))
        out.append(End(offset=(first.line_start, end_offset), tag=tag))
        return out

    def _close_container_event(self, c: OpenContainer, end_offset: int) -> Event:
        if isinstance(c, OpenBlockQuote):
            return End(offset=(c.open_start, end_offset), tag=BlockQuote(kind=c.kind))
        if isinstance(c, OpenList):
            return End(
                offset=(c.open_start, end_offset),
                tag=List(
                    start=c.start if c.is_ordered else None,
                    tight=not c.is_loose,
                ),
            )
        if isinstance(c, OpenItem):
            return End(offset=(c.open_start, end_offset), tag=Item())
        raise TypeError(c)


_GFM_ADMONITION_TAGS = {
    'note': BlockQuoteKind.NOTE,
    'tip': BlockQuoteKind.TIP,
    'important': BlockQuoteKind.IMPORTANT,
    'warning': BlockQuoteKind.WARNING,
    'caution': BlockQuoteKind.CAUTION,
}


def _scan_blockquote_kind_consuming(ls: LineStart) -> BlockQuoteKind | None:
    """
    Look at the remainder of the line for `[!NAME]` followed only by whitespace through EOL. On match, consume the
    marker text and return the kind. Otherwise leave `ls` unchanged.
    """

    save = ls.clone()
    rem = ls.remaining()
    if not rem.startswith('[!'):
        return None
    close_ix = rem.find(']', 2)
    if close_ix < 0:
        return None
    name = rem[2:close_ix].lower()
    kind = _GFM_ADMONITION_TAGS.get(name)
    if kind is None:
        return None
    # Tail of the line (after the `]`) must be whitespace-only.
    tail = rem[close_ix + 1:]
    if tail.strip() != '':
        ls.restore(save)
        return None
    # Consume to end of line.
    ls.advance(len(rem))
    return kind


def _leading_indent(line: str, cap: int = 4) -> int:
    cols = 0
    i = 0
    n = len(line)
    while i < n and cols < cap:
        c = line[i]
        if c == ' ':
            cols += 1
            i += 1
        elif c == '\t':
            cols += 4 - (cols % 4)
            i += 1
        else:
            break
    return cols
