"""
Open-leaf-block state types.

One frozen state class per kind of multi-line leaf block. The BlockMachine owns a single `OpenLeaf | None` (with a stack
of open containers above the leaf).

Conventions:

- Each `OpenLeaf` is mutable in the limited sense that the BlockMachine `dc.replace`s it to push new lines onto it.
  (Pulldown-cmark stores everything in a flat `Tree<Item>`; we hold per-block state inline for clarity.)
- `line_start` / `line_next` mean absolute character offsets into the parser's logical input stream. `line_next` is the
  offset of the first character *after* this line's trailing newline (or end of input).
"""
from omlish import dataclasses as dc
from omlish import lang

from ..events import Alignment


##


@dc.dataclass(frozen=True)
class BufferedLine:
    text: str        # the line content, with the trailing newline stripped
    line_start: int  # absolute offset of `text[0]`
    line_next: int   # absolute offset of the first character after the trailing newline


class OpenLeaf(lang.Abstract):
    """
    Marker base for open-leaf-block state. Variants below are independent frozen dataclasses; we use an empty abstract
    base for nominal typing rather than a union alias (project-wide preference for capability markers).
    """


@dc.dataclass(frozen=True)
class OpenParagraph(OpenLeaf):
    """
    A paragraph. Buffered until close because the next line may promote it to a setext heading or extend it (lazy
    continuation). Cf. pulldown-cmark/src/firstpass.rs::parse_paragraph.
    """

    lines: tuple[BufferedLine, ...]


@dc.dataclass(frozen=True)
class OpenFencedCode(OpenLeaf):
    """
    A fenced code block. Cf. pulldown-cmark/src/firstpass.rs::parse_fenced_code_block.

    Content lines accumulate, with the open-fence's leading-indent count subtracted from each
    content line's leading spaces (CommonMark §4.5: "If the leading code fence is indented N
    spaces, then up to N spaces of indentation are removed from each line of the content").
    """

    fence_char: str
    fence_length: int
    fence_indent: int
    info: str
    open_start: int  # offset of the open-fence line's first non-indent char
    open_next: int   # offset just past the open-fence line's newline
    content: tuple[BufferedLine, ...]  # buffered content lines, in order


@dc.dataclass(frozen=True)
class OpenIndentedCode(OpenLeaf):
    """
    An indented code block. Cf. pulldown-cmark/src/firstpass.rs::parse_indented_code_block.

    Trailing blank lines are stripped at close. The block ends when a non-blank line with less than 4 columns of leading
    indent appears.
    """

    lines: tuple[BufferedLine, ...]  # the leading 4 indent-columns are stripped from `text`


@dc.dataclass(frozen=True)
class OpenHtmlBlock(OpenLeaf):
    """
    An HTML block. Cf. pulldown-cmark/src/firstpass.rs::parse_html_block_type_1_to_5 and parse_html_block_type_6_or_7.
    `html_type` is one of 1..7 per the CommonMark spec.

    Content lines accumulate verbatim; close is triggered by a per-type marker on a line (types 1-5) or by a blank line
    (types 6, 7).
    """

    html_type: int
    open_start: int
    lines: tuple[BufferedLine, ...]


@dc.dataclass(frozen=True)
class OpenTable(OpenLeaf):
    """
    A GFM table mid-parse. The head + alignment rows have been seen and emitted as events; the open-leaf state tracks
    the alignment metadata so subsequent body rows can be parsed correctly, and remembers the absolute open offset for
    the eventual close event.

    Cf. pulldown-cmark/src/firstpass.rs::parse_table.
    """

    alignments: tuple[Alignment, ...]
    open_start: int
