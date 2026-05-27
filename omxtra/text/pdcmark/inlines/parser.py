"""
Inline parser entry point.

Three-stage pipeline per block:

  1. `tokenize_inline` - walks the block's text producing a flat list of `InlineNode`s, resolving
     confident constructs (code, escapes, entities, autolinks, inline HTML, breaks, link-suffix syntax) and leaving
     emphasis as raw `DelimNode` placeholders and link bracket-pairs as `LinkOpenNode`/`LinkCloseNode` placeholders.
  2. `resolve_links` - pairs link openers/closers, looks up refdefs (consulting the fuel guard and
     the broken-link resolver), wraps matched pairs into `LinkGroup` nodes. Unmatched fall back to text.
  3. `resolve_emphasis` - pairs delimiter runs per CommonMark Appendix A, recurses into link-group
     children. Wraps matched pairs into `EmphasisGroup`s.
  4. `_emit_events` - walks the resolved tree of nodes and produces `Event`s.

Cf. pulldown-cmark/src/parse.rs::{handle_inline_pass1, handle_emphasis_and_hard_break} - same roles, distributed
differently. Pulldown does link recognition + the first emphasis-marker pass together in `handle_inline_pass1`; we split
link from emphasis into two explicit passes that operate on the same flat node list.
"""
import typing as ta

from ..blocks.leaves import BufferedLine
from ..blocks.refdefs import RefDefs
from ..events import Code
from ..events import Emphasis
from ..events import End
from ..events import Event
from ..events import HardBreak
from ..events import Image
from ..events import InlineHtml
from ..events import Link
from ..events import LinkType
from ..events import SoftBreak
from ..events import Start
from ..events import Strikethrough
from ..events import Strong
from ..events import Tag
from ..events import Text
from ..options import Options
from .emphasis import resolve_emphasis
from .links import Fuel
from .links import resolve_links
from .nodes import AutolinkNode
from .nodes import CodeNode
from .nodes import EmphasisGroup
from .nodes import HardBreakNode
from .nodes import HtmlNode
from .nodes import InlineNode
from .nodes import LinkGroup
from .nodes import SoftBreakNode
from .nodes import TextNode
from .tokenize import tokenize_inline


##


class InlineParser:
    def __init__(
            self,
            options: Options,
            refdefs: RefDefs | None = None,
            fuel: Fuel | None = None,
    ) -> None:
        super().__init__()

        self._options = options
        self._refdefs = refdefs if refdefs is not None else RefDefs()
        self._fuel = fuel if fuel is not None else Fuel(remaining=options.link_ref_expansion_min)

    @property
    def refdefs(self) -> RefDefs:
        return self._refdefs

    @property
    def fuel(self) -> Fuel:
        return self._fuel

    def parse(self, lines: ta.Sequence[BufferedLine]) -> list[Event]:
        if not lines:
            return []
        nodes = tokenize_inline(tuple(lines), strikethrough=self._options.strikethrough)
        nodes = resolve_links(
            nodes,
            refdefs=self._refdefs,
            fuel=self._fuel,
            broken_link_resolver=self._options.broken_link_resolver,
        )
        # Resolve emphasis on the top-level list AND recursively inside link / image groups.
        _resolve_emphasis_recursive(nodes)
        out: list[Event] = []
        _emit_events(nodes, out)
        return out


##


def _resolve_emphasis_recursive(nodes: list[InlineNode]) -> None:
    resolve_emphasis(nodes)

    for n in nodes:
        if isinstance(n, LinkGroup):
            _resolve_emphasis_recursive(n.children)

        elif isinstance(n, EmphasisGroup):
            _resolve_emphasis_recursive(n.children)


def _emit_events(nodes: ta.Iterable[InlineNode], out: list[Event]) -> None:
    tag: Tag

    for n in nodes:
        if isinstance(n, TextNode):
            if n.text:
                out.append(Text(offset=n.offset, text=n.text))

        elif isinstance(n, CodeNode):
            out.append(Code(offset=n.offset, text=n.text))

        elif isinstance(n, HtmlNode):
            out.append(InlineHtml(offset=n.offset, text=n.text))

        elif isinstance(n, AutolinkNode):
            dest = ('mailto:' + n.target) if n.is_email else n.target
            link_type = LinkType.EMAIL if n.is_email else LinkType.AUTOLINK
            tag = Link(link_type=link_type, dest_url=dest, title='', id='')
            out.append(Start(offset=n.offset, tag=tag))
            out.append(Text(offset=n.offset, text=n.target))
            out.append(End(offset=n.offset, tag=tag))

        elif isinstance(n, SoftBreakNode):
            out.append(SoftBreak(offset=n.offset))

        elif isinstance(n, HardBreakNode):
            out.append(HardBreak(offset=n.offset))

        elif isinstance(n, EmphasisGroup):
            if n.kind == 'strong':
                tag = Strong()
            elif n.kind == 'strikethrough':
                tag = Strikethrough()
            else:
                tag = Emphasis()
            out.append(Start(offset=n.offset, tag=tag))
            _emit_events(n.children, out)
            out.append(End(offset=n.offset, tag=tag))

        elif isinstance(n, LinkGroup):
            tag = (
                Image(link_type=n.link_type, dest_url=n.dest_url, title=n.title, id=n.id)
                if n.is_image
                else Link(link_type=n.link_type, dest_url=n.dest_url, title=n.title, id=n.id)
            )
            out.append(Start(offset=n.offset, tag=tag))
            _emit_events(n.children, out)
            out.append(End(offset=n.offset, tag=tag))

        else:
            raise TypeError(n)
