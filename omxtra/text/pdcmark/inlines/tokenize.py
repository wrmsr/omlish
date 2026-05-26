"""
First-pass inline tokenizer.

Takes a block's `BufferedLine` tuple, joins them into a logical string (with line breaks represented internally), and
walks the string producing a flat list of `InlineNode`s. Confident constructs (code spans, escapes, entities, autolinks,
inline HTML, soft / hard breaks) are resolved here; emphasis is left as `DelimNode` placeholders for the resolution
pass.

Source offsets are tracked via a small position-to-offset lookup table built during joining.

Cf. pulldown-cmark/src/parse.rs::handle_inline_pass1 — same role and same construct precedences, but operating on a
fresh joined string rather than mutating a tree.
"""
import unicodedata

from omlish import dataclasses as dc

from ..blocks.leaves import BufferedLine
from ..scanning.autolinks import scan_autolink
from ..scanning.entities import scan_entity
from ..scanning.escapes import is_escapable
from ..scanning.inlinehtml import scan_inline_html
from ..scanning.links import scan_link_destination
from ..scanning.links import scan_link_label
from ..scanning.links import scan_link_title
from .nodes import AutolinkNode
from .nodes import CodeNode
from .nodes import DelimNode
from .nodes import HardBreakNode
from .nodes import HtmlNode
from .nodes import InlineNode
from .nodes import LinkCloseNode
from .nodes import LinkOpenNode
from .nodes import SoftBreakNode
from .nodes import TextNode


##


@dc.dataclass(frozen=True)
class _LineInfo:
    joined_start: int  # position in joined text where this line begins
    source_start: int  # original BufferedLine.line_start
    source_next: int   # original BufferedLine.line_next
    text_len: int      # length of `text` in the joined string (after trim)


@dc.dataclass(frozen=True)
class _Joined:
    text: str
    lines: tuple[_LineInfo, ...]
    hard_break_after: tuple[bool, ...]  # parallel to `lines`; True iff a HardBreak follows


def _build_joined(lines: tuple[BufferedLine, ...]) -> _Joined:
    out_parts: list[str] = []
    info: list[_LineInfo] = []
    hard: list[bool] = []
    pos = 0
    last_ix = len(lines) - 1

    for i, ln in enumerate(lines):
        # Strip leading whitespace per CM paragraph rules. Block parsing has already stripped up-to-3-space indentation;
        # what remains here is the line content as it appeared after container markers.
        text = ln.text
        # Leading whitespace stripping happens in the block parser for paragraph emission; for inline parsing we strip
        # again to handle any continuation-line leading whitespace that the block parser didn't (e.g., lazy-continuation
        # lines).
        text = text.lstrip(' \t')

        is_hardbreak = False
        if i < last_ix:
            if text.endswith('\\'):
                # Literal backslash at end of line → hard break, consume the backslash. Only if the backslash isn't
                # itself escaped — CM treats the trailing-`\` form specially and we don't have to worry about
                # double-backslash because we trim only one.
                text = text[:-1]
                is_hardbreak = True
            elif text.endswith('  '):
                # 2+ trailing spaces → hard break.
                text = text.rstrip(' \t')
                is_hardbreak = True
            else:
                # Strip trailing whitespace (it's not significant for non-hard-break case).
                text = text.rstrip(' \t')
        else:
            # Last line — no following line, no hard break. Just strip trailing whitespace.
            text = text.rstrip(' \t')

        info.append(_LineInfo(
            joined_start=pos,
            source_start=ln.line_start,
            source_next=ln.line_next,
            text_len=len(text),
        ))
        hard.append(is_hardbreak)
        out_parts.append(text)
        pos += len(text)
        if i < last_ix:
            out_parts.append('\n')
            pos += 1

    return _Joined(
        text=''.join(out_parts),
        lines=tuple(info),
        hard_break_after=tuple(hard),
    )


def _source_offset(joined: _Joined, p: int) -> int:
    """Map a joined-text position to an absolute source offset."""

    # Linear walk; lines per block are typically few. Could binary-search if it ever matters.
    for li in joined.lines:
        if p < li.joined_start + li.text_len:
            return li.source_start + (p - li.joined_start)
        if p == li.joined_start + li.text_len:
            # On the newline boundary — point at start of the newline char in source. If trailing whitespace was
            # trimmed, the newline is somewhere before line_next; we approximate by using line_next - 1.
            return max(li.source_start, li.source_next - 1)
    # Off the end of joined → end of last line.
    return joined.lines[-1].source_next


##


def tokenize_inline(
        lines: tuple[BufferedLine, ...],
        *,
        strikethrough: bool = False,
) -> list[InlineNode]:
    if not lines:
        return []
    joined = _build_joined(lines)
    nodes: list[InlineNode] = []
    s = joined.text
    n = len(s)

    # Text accumulator — flushed into a TextNode on any non-text token.
    buf: list[str] = []
    buf_start = 0  # joined position where buf started (only valid if buf is non-empty)

    def flush_text() -> None:
        if not buf:
            return
        text = ''.join(buf)
        if text:
            start = _source_offset(joined, buf_start)
            end = _source_offset(joined, buf_start + len(text))
            nodes.append(TextNode(offset=(start, end), text=text))
        buf.clear()

    def emit(node: InlineNode) -> None:
        flush_text()
        nodes.append(node)

    i = 0
    while i < n:
        c = s[i]

        # Newline boundary — soft or hard break.
        if c == '\n':
            # Determine which line transition this newline marks. Find the line whose joined_start + text_len == i.
            line_ix = _line_index_at_newline(joined, i)
            is_hard = joined.hard_break_after[line_ix] if line_ix is not None else False
            line_end_source = (
                joined.lines[line_ix].source_next
                if line_ix is not None else _source_offset(joined, i + 1)
            )
            line_start_source = (
                joined.lines[line_ix].source_start + joined.lines[line_ix].text_len
                if line_ix is not None else _source_offset(joined, i)
            )
            if is_hard:
                emit(HardBreakNode(offset=(line_start_source, line_end_source)))
            else:
                emit(SoftBreakNode(offset=(line_start_source, line_end_source)))
            i += 1
            continue

        # Backslash escape.
        if c == '\\' and i + 1 < n:
            nxt = s[i + 1]
            if nxt == '\n':
                # Backslash before EOL — already handled at trim time as a hard break (the `\` was consumed). This
                # branch shouldn't normally hit, but if it does we treat as text.
                if not buf:
                    buf_start = i
                buf.append(c)
                i += 1
                continue
            if is_escapable(nxt):
                if not buf:
                    buf_start = i
                buf.append(nxt)
                i += 2
                continue
            # Fall through — backslash before non-escapable char is literal.

        # Entity reference.
        if c == '&':
            m = scan_entity(s, i)
            if m is not None:
                if not buf:
                    buf_start = i
                buf.append(m.decoded)
                # Stretch buf_start to point at decoded content; tracker continues from m.end.
                i = m.end
                continue

        # Code span.
        if c == '`':
            run = _backtick_run(s, i)
            close = _find_matching_backtick_close(s, i + run, run)
            if close is not None:
                content = s[i + run:close]
                content = _normalize_code_span(content)
                start_src = _source_offset(joined, i)
                end_src = _source_offset(joined, close + run)
                emit(CodeNode(offset=(start_src, end_src), text=content))
                i = close + run
                continue
            # No matching close — treat backticks as text.
            if not buf:
                buf_start = i
            buf.append(s[i:i + run])
            i += run
            continue

        # Autolink or inline HTML or literal `<`.
        if c == '<':
            al = scan_autolink(s, i)
            if al is not None:
                start_src = _source_offset(joined, i)
                end_src = _source_offset(joined, al.end)
                emit(AutolinkNode(offset=(start_src, end_src), target=al.target, is_email=al.is_email))
                i = al.end
                continue
            html_m = scan_inline_html(s, i)
            if html_m is not None:
                start_src = _source_offset(joined, i)
                end_src = _source_offset(joined, html_m.end)
                emit(HtmlNode(offset=(start_src, end_src), text=s[i:html_m.end]))
                i = html_m.end
                continue

        # Image open `![` (must check before plain `!`).
        if c == '!' and i + 1 < n and s[i + 1] == '[':
            start_src = _source_offset(joined, i)
            end_src = _source_offset(joined, i + 2)
            emit(LinkOpenNode(offset=(start_src, end_src), is_image=True))
            i += 2
            continue

        # Link open `[`.
        if c == '[':
            start_src = _source_offset(joined, i)
            end_src = _source_offset(joined, i + 1)
            emit(LinkOpenNode(offset=(start_src, end_src), is_image=False))
            i += 1
            continue

        # Link close `]` — also peeks ahead for the link suffix.
        if c == ']':
            close_start_src = _source_offset(joined, i)  # noqa
            close_node, consumed_to = _scan_link_suffix(s, i, joined)
            emit(close_node)
            i = consumed_to
            continue

        # Emphasis delimiter. `~` is only a delim if the strikethrough option is enabled.
        if c == '*' or c == '_' or (c == '~' and strikethrough):
            run_end = i
            while run_end < n and s[run_end] == c:
                run_end += 1
            prev_c = s[i - 1] if i > 0 else '\n'
            next_c = s[run_end] if run_end < n else '\n'
            can_open, can_close = _flanking(c, prev_c, next_c)
            start_src = _source_offset(joined, i)
            end_src = _source_offset(joined, run_end)
            emit(DelimNode(
                offset=(start_src, end_src),
                char=c,
                count=run_end - i,
                can_open=can_open,
                can_close=can_close,
            ))
            i = run_end
            continue

        # Plain text accumulation.
        if not buf:
            buf_start = i
        buf.append(c)
        i += 1

    flush_text()
    return nodes


##


def _backtick_run(s: str, i: int) -> int:
    n = len(s)
    j = i
    while j < n and s[j] == '`':
        j += 1
    return j - i


def _find_matching_backtick_close(s: str, start: int, run_len: int) -> int | None:
    """Find the start position of a run of exactly `run_len` backticks starting at `s[start:]`."""

    n = len(s)
    i = start
    while i < n:
        # Find the next backtick.
        bt = s.find('`', i)
        if bt < 0:
            return None
        # Measure the run.
        j = bt
        while j < n and s[j] == '`':
            j += 1
        if j - bt == run_len:
            return bt
        i = j
    return None


def _normalize_code_span(content: str) -> str:
    """
    CM §6.3 normalization: turn line breaks into spaces; if there's at least one non-space char and the content starts
    AND ends with a single space, strip the surrounding spaces.
    """

    # Replace line breaks with spaces.
    content = content.replace('\n', ' ')
    if (
        len(content) >= 2
        and content[0] == ' '
        and content[-1] == ' '
        and any(c != ' ' for c in content)
    ):
        return content[1:-1]
    return content


def _flanking(c: str, prev_c: str, next_c: str) -> tuple[bool, bool]:
    """
    Compute `can_open` and `can_close` for an emphasis delimiter run.

    Direct port of CommonMark §6.4 "left-flanking" / "right-flanking" definitions plus the intraword-underscore rule.
    See pulldown-cmark/src/parse.rs::{delim_run_can_open, delim_run_can_close}.
    """

    prev_ws = _is_unicode_whitespace(prev_c)
    next_ws = _is_unicode_whitespace(next_c)
    prev_punct = _is_unicode_punct(prev_c)
    next_punct = _is_unicode_punct(next_c)

    left_flanking = (
        not next_ws
        and (not next_punct or prev_ws or prev_punct)
    )
    right_flanking = (
        not prev_ws
        and (not prev_punct or next_ws or next_punct)
    )

    if c == '*':
        can_open = left_flanking
        can_close = right_flanking
    else:
        # Underscore: intraword underscores are neither opening nor closing.
        can_open = left_flanking and (not right_flanking or prev_punct)
        can_close = right_flanking and (not left_flanking or next_punct)

    return can_open, can_close


def _is_unicode_whitespace(c: str) -> bool:
    if c == '':
        return True
    if c in ' \t\n\v\f\r':
        return True
    # CM defines unicode whitespace as `Zs` plus tab/CR/LF/FF/VT.
    return unicodedata.category(c).startswith('Z')


def _is_unicode_punct(c: str) -> bool:
    if c == '':
        return False
    # CM uses ASCII-punctuation OR Unicode P*-category.
    if c in '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~':
        return True
    cat = unicodedata.category(c)
    return cat.startswith('P') or cat.startswith('S')


def _line_index_at_newline(joined: _Joined, pos: int) -> int | None:
    for ix, li in enumerate(joined.lines):
        if li.joined_start + li.text_len == pos:
            return ix
    return None


def _scan_link_suffix(s: str, close_pos: int, joined: _Joined) -> tuple[LinkCloseNode, int]:
    """
    Inspect what follows a `]` at `s[close_pos]` to determine the link-close kind.

    Returns (LinkCloseNode, new_position_in_joined). The new position is the index just past any consumed suffix syntax.
    If no suffix matches, only the `]` itself is consumed and the close node is tagged as 'shortcut' — link resolution
    will try refdefs later.

    The literal source text from `]` through the consumed suffix is captured in `raw_consumed` so a resolution failure
    can emit it back as plain text.
    """

    n = len(s)
    close_src = _source_offset(joined, close_pos)
    close_src_end = _source_offset(joined, close_pos + 1)
    after = close_pos + 1
    if after >= n:
        return LinkCloseNode(
            offset=(close_src, close_src_end),
            consumed_end=close_src_end,
            kind='shortcut',
            raw_consumed=']',
        ), after

    nxt = s[after]

    # Inline link / image: `(dest "title")`.
    if nxt == '(':
        result = _try_parse_inline_link(s, after)
        if result is not None:
            dest, title, end_pos = result
            end_src = _source_offset(joined, end_pos)
            return LinkCloseNode(
                offset=(close_src, close_src_end),
                consumed_end=end_src,
                kind='inline',
                raw_consumed=s[close_pos:end_pos],
                dest_url=dest,
                title=title,
            ), end_pos
        # Fall through — `(` without a valid link → shortcut form.

    # Reference link: `[label]` or `[]`.
    if nxt == '[':
        # `[]` → collapsed.
        if after + 1 < n and s[after + 1] == ']':
            end_pos = after + 2
            end_src = _source_offset(joined, end_pos)
            return LinkCloseNode(
                offset=(close_src, close_src_end),
                consumed_end=end_src,
                kind='collapsed',
                raw_consumed=s[close_pos:end_pos],
            ), end_pos
        # `[label]` → reference.
        label_scan = scan_link_label(s, after)
        if label_scan is not None:
            end_pos = label_scan.end
            end_src = _source_offset(joined, end_pos)
            return LinkCloseNode(
                offset=(close_src, close_src_end),
                consumed_end=end_src,
                kind='reference',
                raw_consumed=s[close_pos:end_pos],
                label=label_scan.raw,
            ), end_pos

    # Default — shortcut form (try inner text against refdefs at resolution time).
    return LinkCloseNode(
        offset=(close_src, close_src_end),
        consumed_end=close_src_end,
        kind='shortcut',
        raw_consumed=']',
    ), after


def _try_parse_inline_link(s: str, paren_pos: int) -> tuple[str, str, int] | None:
    """Parse `(dest "title")` starting at the `(`. Returns (dest, title, end_pos_after_paren)."""

    n = len(s)
    i = paren_pos + 1  # past `(`
    # Optional whitespace (including up to 1 newline).
    i = _consume_link_ws(s, i, allow_nl=True)
    if i >= n:
        return None
    if s[i] == ')':
        return '', '', i + 1
    # Destination — may or may not be present.
    dest = ''
    if s[i] != ')':
        dest_scan = scan_link_destination(s, i)
        if dest_scan is None:
            return None
        dest = dest_scan.dest
        i = dest_scan.end
    # Optional whitespace before title.
    pre_title = i
    i = _consume_link_ws(s, i, allow_nl=True)
    title = ''
    if i < n and s[i] in '"\'(':
        title_scan = scan_link_title(s, i)
        if title_scan is not None:
            # Title valid; require ws-then-`)` after.
            title = title_scan.title
            i = title_scan.end
            i = _consume_link_ws(s, i, allow_nl=True)
        else:
            # Title-shaped but invalid — fail the whole inline link.
            return None
    else:
        i = pre_title  # no title; rewind ws-skip if it ate nothing useful
        i = _consume_link_ws(s, i, allow_nl=True)
    if i >= n or s[i] != ')':
        return None
    return dest, title, i + 1


def _consume_link_ws(s: str, i: int, *, allow_nl: bool) -> int:
    n = len(s)
    saw_nl = False
    while i < n:
        c = s[i]
        if c == ' ' or c == '\t':
            i += 1
            continue
        if c == '\n' and allow_nl and not saw_nl:
            i += 1
            saw_nl = True
            continue
        break
    return i
