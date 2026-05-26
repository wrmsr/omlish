"""
Runner for pulldown-cmark-style `.txt` spec fixture files.

Format (cf. CommonMark dingus / pulldown-cmark/pulldown-cmark/specs/*.txt):

    ```````````````````````````````` example
    <markdown source>
    .
    <expected html>
    ````````````````````````````````

The fence is a long run of backticks (>= 3, in practice 32). The opening fence is followed by a keyword — `example` for
tests that run, `DISABLED example` (or `... DISABLED`) for tests skipped. Inside, a `.` on its own line separates the
markdown source from the expected HTML. Section titles (setext-style `=== ` underlines or `## …` headings) are picked up
as group names for nicer pytest IDs.

Tabs in spec fixtures are written as the literal arrow character `→` (U+2192) and substituted back to `\\t` at load
time, matching how the CommonMark spec source is authored.
"""
import io
import os.path
import re
import typing as ta

from omlish import dataclasses as dc


##


# Opening fence: at least 3 backticks followed by anything before EOL. We match `example` and `DISABLED example` (in
# either order, case-insensitive).
_FENCE_RE = re.compile(r'^(`{3,})\s*(.*)$')

_SEPARATOR_LINE = '.'

# Tab placeholder used in the upstream spec source.
_TAB_ARROW = '→'


@dc.dataclass(frozen=True)
class SpecCase:
    file: str           # short file label (basename)
    index: int          # 1-based ordinal within the file
    section: str        # nearest preceding section header; '' if none
    line: int           # 1-based line number of the opening fence
    markdown: str
    expected_html: str
    disabled: bool = False
    keyword: str = 'example'  # the post-fence keyword(s), case-preserved


def load_spec_file(path: str) -> list[SpecCase]:
    with open(path, encoding='utf-8') as f:
        text = f.read()
    return parse_spec_text(text, file=os.path.basename(path))


def parse_spec_text(text: str, *, file: str = '<text>') -> list[SpecCase]:
    cases: list[SpecCase] = []
    lines = text.splitlines()
    n = len(lines)

    section = ''
    i = 0
    case_no = 0
    while i < n:
        line = lines[i]

        # Detect section header (atx `#`/`##`/... or setext `===` / `---` underline).
        sec = _try_section_header(lines, i)
        if sec is not None:
            section, advance = sec
            i += advance
            continue

        m = _FENCE_RE.match(line)
        if m:
            fence = m.group(1)
            keyword = m.group(2).strip()
            if 'example' not in keyword.lower():
                # A code fence in the documentation prose, not a test case. Skip until close.
                i = _skip_to_close_fence(lines, i + 1, fence)
                continue

            disabled = 'disabled' in keyword.lower()
            start_line = i + 1

            md_buf = io.StringIO()
            html_buf = io.StringIO()
            in_md = True
            i += 1
            while i < n:
                inner = lines[i]
                if inner.startswith(fence):
                    break
                if in_md and inner == _SEPARATOR_LINE:
                    in_md = False
                    i += 1
                    continue
                (md_buf if in_md else html_buf).write(_decode_tabs(inner))
                (md_buf if in_md else html_buf).write('\n')
                i += 1

            case_no += 1
            cases.append(SpecCase(
                file=file,
                index=case_no,
                section=section,
                line=start_line,
                markdown=md_buf.getvalue(),
                expected_html=html_buf.getvalue(),
                disabled=disabled,
                keyword=keyword,
            ))
            i += 1  # past closing fence
            continue

        i += 1

    return cases


def _decode_tabs(s: str) -> str:
    if _TAB_ARROW in s:
        return s.replace(_TAB_ARROW, '\t')
    return s


def _try_section_header(lines: ta.Sequence[str], i: int) -> tuple[str, int] | None:
    line = lines[i]

    # ATX-style: `# heading` / `## heading` / ...
    if line.startswith('#'):
        m = re.match(r'^(#{1,6})\s+(.*?)\s*#*\s*$', line)
        if m:
            return m.group(2), 1

    # Setext-style: title line followed by an underline of `=` or `-`.
    if i + 1 < len(lines) and line.strip():
        nxt = lines[i + 1]
        if nxt and (set(nxt.strip()) <= {'='} or set(nxt.strip()) <= {'-'}) and len(nxt.strip()) >= 3:
            return line.strip(), 2

    return None


def _skip_to_close_fence(lines: ta.Sequence[str], start: int, fence: str) -> int:
    i = start
    n = len(lines)
    while i < n:
        if lines[i].startswith(fence):
            return i + 1
        i += 1
    return n


##


def pytest_id_for(case: SpecCase) -> str:
    """Stable pytest test ID for a case."""

    return f'{case.file}:{case.index}'
