import typing as ta

from omlish import check
from omlish import lang

from ..blank import BlankContent
from ..code import BlockCodeContent
from ..code import InlineCodeContent
from ..containers import BlocksContent
from ..containers import FlowContent
from ..content import Content
from ..emphasis import BoldContent
from ..emphasis import BoldItalicContent
from ..emphasis import ItalicContent
from ..itemlist import ItemListContent
from ..link import LinkContent
from ..quote import QuoteContent
from ..section import SectionContent
from ..text import TextContent
from .types import ContentParser
from .types import UnsupportedMarkdownError


if ta.TYPE_CHECKING:
    import markdown_it as md
else:
    md = lang.proxy_import('markdown_it')


##


class MarkdownContentParser(ContentParser, lang.Final):
    def __init__(self, *, parser: md.MarkdownIt | None = None) -> None:
        super().__init__()

        if parser is None:
            parser = md.MarkdownIt()
        self._parser: md.MarkdownIt = parser

    #

    def parse(self, src: str) -> Content:
        tokens = self._parser.parse(src)
        blocks = _parse_blocks(tokens, 0, len(tokens))
        return _group_sections_from_blocks(blocks)

    #

    def __repr__(self) -> str:
        return f'{type(self).__name__}()'


##


def _find_matching_close(tokens: list, start: int) -> int:
    """Given tokens[start] is an open token (nesting=1), find its matching close (nesting=-1)."""

    check.arg(tokens[start].nesting == 1)
    depth = 1
    i = start + 1
    while i < len(tokens):
        if tokens[i].nesting == 1:
            depth += 1
        elif tokens[i].nesting == -1:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError(f'No matching close token for {tokens[start].type!r} at index {start}')


##


def _parse_blocks(tokens: list, start: int, end: int) -> list[Content | tuple[int, str]]:
    """
    Parse block-level tokens into content nodes.

    Headings produce (level, header_text) tuples for later section grouping.
    """

    blocks: list[Content | tuple[int, str]] = []
    i = start

    while i < end:
        token = tokens[i]
        tt = token.type

        if tt == 'paragraph_open':
            close = _find_matching_close(tokens, i)
            inline_token = _find_inline_token(tokens, i + 1, close)
            blocks.append(_parse_inline(inline_token.children or []))
            i = close + 1

        elif tt == 'heading_open':
            close = _find_matching_close(tokens, i)
            level = int(token.tag[1:])  # h1 -> 1, h2 -> 2, etc.
            inline_token = _find_inline_token(tokens, i + 1, close)
            header_text = _extract_plain_text(inline_token.children or [])
            blocks.append((level, header_text))
            i = close + 1

        elif tt == 'blockquote_open':
            close = _find_matching_close(tokens, i)
            inner = _parse_blocks(tokens, i + 1, close)
            body = _simplify_blocks(inner)
            blocks.append(QuoteContent(body))
            i = close + 1

        elif tt in ('bullet_list_open', 'ordered_list_open'):
            close = _find_matching_close(tokens, i)
            style: ta.Literal['-', '#'] = '-' if tt == 'bullet_list_open' else '#'
            items = _parse_list_items(tokens, i + 1, close)
            blocks.append(ItemListContent(items, style=style))
            i = close + 1

        elif tt == 'fence':
            lang_str = token.info.strip() or None
            blocks.append(BlockCodeContent(token.content, lang=lang_str))
            i += 1

        elif tt == 'code_block':
            blocks.append(BlockCodeContent(token.content))
            i += 1

        elif tt == 'hr':
            blocks.append(BlankContent())
            i += 1

        else:
            raise UnsupportedMarkdownError(tt)

    return blocks


def _find_inline_token(tokens: list, start: int, end: int) -> ta.Any:
    """Find the single 'inline' token between start and end."""

    for i in range(start, end):
        if tokens[i].type == 'inline':
            return tokens[i]
    raise ValueError(f'No inline token found between indices {start} and {end}')


def _parse_list_items(tokens: list, start: int, end: int) -> list[Content]:
    """Parse list_item_open/close pairs into a list of Content."""

    items: list[Content] = []
    i = start

    while i < end:
        token = tokens[i]
        if token.type == 'list_item_open':
            close = _find_matching_close(tokens, i)
            inner = _parse_blocks(tokens, i + 1, close)
            items.append(_simplify_blocks(inner))
            i = close + 1
        else:
            raise UnsupportedMarkdownError(token.type, 'unexpected token inside list')

    return items


##


def _parse_inline(children: list) -> Content:
    """
    Parse inline tokens into content.

    Softbreaks split inline content into separate TextContent nodes within a FlowContent.
    """

    parts: list[Content] = []
    i = 0

    while i < len(children):
        token = children[i]
        tt = token.type

        if tt == 'text':
            if token.content:
                parts.append(TextContent(token.content))
            i += 1

        elif tt == 'code_inline':
            parts.append(InlineCodeContent(token.content))
            i += 1

        elif tt == 'softbreak':
            i += 1

        elif tt == 'hardbreak':
            parts.append(BlankContent())
            i += 1

        elif tt == 'strong_open':
            content, next_i = _parse_emphasis(children, i, 'strong_open', 'strong_close')
            parts.append(content)
            i = next_i

        elif tt == 'em_open':
            content, next_i = _parse_emphasis(children, i, 'em_open', 'em_close')
            parts.append(content)
            i = next_i

        elif tt == 'link_open':
            content, next_i = _parse_link(children, i)
            parts.append(content)
            i = next_i

        elif tt in ('image', 'html_inline', 'text_special'):
            raise UnsupportedMarkdownError(tt)

        else:
            raise UnsupportedMarkdownError(tt)

    return _simplify_flow(parts)


def _parse_emphasis(children: list, start: int, open_type: str, close_type: str) -> tuple[Content, int]:
    """
    Parse an emphasis span (bold/italic).

    Returns the content and the index after the close token.
    """

    # Find matching close
    depth = 1
    i = start + 1
    while i < len(children):
        if children[i].type == open_type and children[i].nesting == 1:
            depth += 1
        elif children[i].type == close_type and children[i].nesting == -1:
            depth -= 1
            if depth == 0:
                break
        i += 1
    else:
        raise ValueError(f'No matching {close_type!r} for {open_type!r} at index {start}')

    close_idx = i
    interior = children[start + 1:close_idx]

    # Check for bold-italic pattern: strong wrapping em (or em wrapping strong) with only empty text around
    bold_italic = _try_bold_italic(interior, open_type)
    if bold_italic is not None:
        return bold_italic, close_idx + 1

    # Otherwise, interior must be plain text only
    text = _extract_emphasis_text(interior, open_type)

    if open_type == 'strong_open':
        return BoldContent(text), close_idx + 1
    else:
        return ItalicContent(text), close_idx + 1


def _try_bold_italic(interior: list, outer_type: str) -> Content | None:
    """
    Detect the bold-italic pattern where one emphasis type wraps the other.

    E.g. ***text*** produces: em_open, [text(''),] strong_open, text('...'), strong_close, [text(''),] em_close
    """

    inner_open_type: str
    inner_close_type: str
    if outer_type == 'strong_open':
        inner_open_type = 'em_open'
        inner_close_type = 'em_close'
    elif outer_type == 'em_open':
        inner_open_type = 'strong_open'
        inner_close_type = 'strong_close'
    else:
        return None

    # Filter out empty text nodes
    non_empty = [t for t in interior if not (t.type == 'text' and t.content == '')]

    if len(non_empty) < 2:
        return None

    if non_empty[0].type != inner_open_type or non_empty[-1].type != inner_close_type:
        return None

    # The inner content (between inner open/close) must be plain text only
    inner_content = non_empty[1:-1]
    text_parts: list[str] = []
    for t in inner_content:
        if t.type == 'text':
            text_parts.append(t.content)
        else:
            return None

    return BoldItalicContent(''.join(text_parts))


def _extract_emphasis_text(interior: list, open_type: str) -> str:
    """Extract plain text from emphasis interior. Raises if non-text tokens found."""

    text_parts: list[str] = []
    for t in interior:
        if t.type == 'text':
            text_parts.append(t.content)
        elif t.type == 'softbreak':
            text_parts.append(' ')
        else:
            kind = open_type.removesuffix('_open')
            raise UnsupportedMarkdownError(
                t.type,
                f'nested formatting inside {kind}: emphasis content types only accept plain strings',
            )
    return ''.join(text_parts)


def _parse_link(children: list, start: int) -> tuple[Content, int]:
    """Parse a link_open/link_close pair. Returns (LinkContent, next_index)."""

    # Find matching link_close
    depth = 1
    i = start + 1
    while i < len(children):
        if children[i].type == 'link_open' and children[i].nesting == 1:
            depth += 1
        elif children[i].type == 'link_close' and children[i].nesting == -1:
            depth -= 1
            if depth == 0:
                break
        i += 1
    else:
        raise ValueError(f'No matching link_close for link_open at index {start}')

    close_idx = i
    interior = children[start + 1:close_idx]

    url = check.isinstance(children[start].attrs.get('href', ''), str)

    # Collect link text - must be plain text only
    text_parts: list[str] = []
    for t in interior:
        if t.type == 'text':
            text_parts.append(t.content)
        elif t.type == 'softbreak':
            text_parts.append(' ')
        else:
            raise UnsupportedMarkdownError(
                t.type,
                'link text contains formatting that cannot be represented',
            )

    title = ''.join(text_parts) or None

    return LinkContent(url, title=title), close_idx + 1


##


def _extract_plain_text(children: list) -> str:
    """Extract plain text from inline children, for heading headers."""

    parts: list[str] = []
    for t in children:
        if t.type == 'text':
            parts.append(t.content)
        elif t.type == 'code_inline':
            parts.append(t.content)
        elif t.type == 'softbreak':
            parts.append(' ')
        else:
            raise UnsupportedMarkdownError(
                t.type,
                'heading contains formatting that cannot be represented as a plain string header',
            )
    return ''.join(parts)


##


def _simplify_flow(parts: list[Content]) -> Content:
    """Wrap a list of inline content parts, avoiding redundant FlowContent nesting."""

    if not parts:
        return FlowContent([])
    if len(parts) == 1:
        return parts[0]
    return FlowContent(parts)


def _simplify_blocks(blocks: list[Content | tuple[int, str]]) -> Content:
    """
    Simplify a list of block-level content nodes.

    Does NOT handle section grouping - this is for blockquote/list item interiors where headings are not expected.
    """

    content_blocks: list[Content] = []
    for b in blocks:
        if isinstance(b, tuple):
            # Heading tuple inside a non-document context (e.g. blockquote) - just emit as text
            _, header_text = b
            content_blocks.append(TextContent(header_text))
        else:
            content_blocks.append(b)

    if not content_blocks:
        return FlowContent([])
    if len(content_blocks) == 1:
        return content_blocks[0]
    return BlocksContent(content_blocks)


##


def _group_sections_from_blocks(blocks: list[Content | tuple[int, str]]) -> Content:
    """
    Group a flat list of blocks (with heading tuples) into hierarchically nested SectionContent.

    Heading tuples are (level: int, header: str). A heading at level N collects all subsequent blocks
    until the next heading of level <= N, and nests them as its body.
    """

    if not blocks:
        return FlowContent([])

    # Check if there are any headings at all
    has_headings = any(isinstance(b, tuple) for b in blocks)
    if not has_headings:
        return _simplify_content_blocks([b for b in blocks if not isinstance(b, tuple)])

    return _group_sections_recursive(blocks, 0, len(blocks))


def _group_sections_recursive(
        blocks: list[Content | tuple[int, str]],
        start: int,
        end: int,
) -> Content:
    """Recursively group blocks into sections based on heading levels."""

    result: list[Content] = []
    i = start

    while i < end:
        b = blocks[i]

        if isinstance(b, tuple):
            level, header = b
            # Find the extent of this section: everything until next heading of same or higher rank
            section_end = i + 1
            while section_end < end:
                nb = blocks[section_end]
                if isinstance(nb, tuple) and nb[0] <= level:
                    break
                section_end += 1

            # Recursively process the section body (may contain sub-headings)
            body_blocks = blocks[i + 1:section_end]
            if body_blocks:
                body = _group_sections_from_blocks(body_blocks)
            else:
                body = FlowContent([])

            result.append(SectionContent(body, header=header))
            i = section_end

        else:
            result.append(b)
            i += 1

    return _simplify_content_blocks(result)


def _simplify_content_blocks(blocks: list[Content]) -> Content:
    """Simplify a list of Content blocks into a single Content node."""

    if not blocks:
        return FlowContent([])
    if len(blocks) == 1:
        return blocks[0]
    return BlocksContent(blocks)


##


def parse_markdown_content(src: str) -> Content:
    """Convenience function to parse markdown into Content."""

    return MarkdownContentParser().parse(src)
