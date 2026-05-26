"""
HTML-block start / end recognition for the 7 CommonMark types.

CommonMark §4.6 defines 7 distinct kinds of HTML block, each with its own start condition and its own end condition:

  type 1 - opens with `<script>` / `<pre>` / `<style>` / `<textarea>` (case-insensitive); closes when the corresponding
           close-tag is matched on the same or a later line.
  type 2 - opens with `<!--`; closes at `-->`.
  type 3 - opens with `<?`; closes at `?>`.
  type 4 - opens with `<!` followed by an ASCII letter; closes at `>`.
  type 5 - opens with `<![CDATA[`; closes at `]]>`.
  type 6 - opens with `<` or `</` followed by a tag from a fixed list of block-level HTML tags, followed by space / tab
           / EOL / `>` / `/>`; closes on a blank line.
  type 7 - opens with any complete HTML open/close tag followed by only whitespace; closes on a blank line. Type 7 may
           not interrupt a paragraph.
"""
import re

from omlish import dataclasses as dc

from .inlinehtml import scan_inline_html


##


# pulldown-cmark/src/scanners.rs::HTML_TAGS - same list. CommonMark §4.6 block-tag set.
_HTML_BLOCK_TAGS = frozenset({
    'address',
    'article',
    'aside',
    'base',
    'basefont',
    'blockquote',
    'body',
    'caption',
    'center',
    'col',
    'colgroup',
    'dd',
    'details',
    'dialog',
    'dir',
    'div',
    'dl',
    'dt',
    'fieldset',
    'figcaption',
    'figure',
    'footer',
    'form',
    'frame',
    'frameset',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'head',
    'header',
    'hr',
    'html',
    'iframe',
    'legend',
    'li',
    'link',
    'main',
    'menu',
    'menuitem',
    'nav',
    'noframes',
    'ol',
    'optgroup',
    'option',
    'p',
    'param',
    'search',
    'section',
    'summary',
    'table',
    'tbody',
    'td',
    'tfoot',
    'th',
    'thead',
    'title',
    'tr',
    'track',
    'ul',
})


_TYPE_1_NAMES = ('script', 'pre', 'style', 'textarea')
_TYPE_1_CLOSE_RES = {
    name: re.compile(r'</' + name + r'(?:[ \t>]|$)', re.IGNORECASE)
    for name in _TYPE_1_NAMES
}


# Late-bound import to avoid cycles (inline_html sits below html_blocks in the dep graph).
def _scan_inline_html_local(s: str, start: int):
    return scan_inline_html(s, start)


@dc.dataclass(frozen=True)
class HtmlBlockStart:
    type: int           # 1..7
    can_interrupt_paragraph: bool  # False only for type 7


# pulldown-cmark/src/scanners.rs::starts_html_block_type_6 and the dispatch logic in
# firstpass.rs::parse_html_block_type_1_to_5 / parse_html_block_type_6_or_7.
def scan_html_block_start(line: str) -> HtmlBlockStart | None:
    """
    Detect an HTML block start. `line` is the content of the line after up-to-3-space indent has been consumed. Returns
    None if no HTML block starts at this position.
    """

    n = len(line)
    if n < 2 or line[0] != '<':
        return None

    # Type 2: <!--
    if line.startswith('<!--'):
        return HtmlBlockStart(type=2, can_interrupt_paragraph=True)

    # Type 5: <![CDATA[
    if line.startswith('<![CDATA['):
        return HtmlBlockStart(type=5, can_interrupt_paragraph=True)

    # Type 4: <! followed by an ASCII letter (uppercase per CM 0.30; relaxed to any letter per current spec).
    if line.startswith('<!') and n >= 3 and line[2].isascii() and line[2].isalpha():
        return HtmlBlockStart(type=4, can_interrupt_paragraph=True)

    # Type 3: <?
    if line.startswith('<?'):
        return HtmlBlockStart(type=3, can_interrupt_paragraph=True)

    # Strip a leading '<' and an optional '/'.
    i = 1
    is_close = (line[i] == '/') if i < n else False
    if is_close:
        i += 1
    j = i
    while j < n and ((line[j].isalnum() and line[j].isascii()) or (j > i and line[j] in '0123456789')):
        j += 1
    if j == i:
        return None
    name = line[i:j].lower()

    # Type 1: <script> / <pre> / <style> / <textarea>, not the close form.
    if not is_close and name in _TYPE_1_NAMES:
        if j == n or line[j] in ' \t>' or line[j:].startswith('/>') or line[j] in '\r\n':
            return HtmlBlockStart(type=1, can_interrupt_paragraph=True)

    # Type 6: any name in the predefined block-tag set, followed by space / tab / EOL / '>' / '/>'.
    if name in _HTML_BLOCK_TAGS:
        if j == n or line[j] in ' \t>' or line[j] in '\r\n' or line[j:].startswith('/>'):
            return HtmlBlockStart(type=6, can_interrupt_paragraph=True)

    # Type 7: any complete HTML tag (open or close) followed by only whitespace until EOL. May not interrupt a
    # paragraph.
    html_match = _scan_inline_html_local(line, 0)
    if html_match is not None and html_match.end <= n:
        tail = line[html_match.end:]
        if tail == '' or tail.lstrip(' \t') == '':
            return HtmlBlockStart(type=7, can_interrupt_paragraph=False)
    return None


# pulldown-cmark/src/firstpass.rs::FirstPass::parse_html_block_type_1_to_5 - same end conditions.
def html_block_close_on_line(html_type: int, line: str) -> bool:
    """
    True iff `line` contains the close marker for `html_type`. Type 6 and 7 close on a blank line; the caller handles
    that separately.
    """

    if html_type == 1:
        # Any of the four type-1 close tags. Case-insensitive.
        return any(_TYPE_1_CLOSE_RES[name].search(line) for name in _TYPE_1_NAMES)
    if html_type == 2:
        return '-->' in line
    if html_type == 3:
        return '?>' in line
    if html_type == 4:
        return '>' in line
    if html_type == 5:
        return ']]>' in line
    return False  # types 6 / 7 close on blank line


def html_block_closes_on_blank_line(html_type: int) -> bool:
    return html_type in (6, 7)
