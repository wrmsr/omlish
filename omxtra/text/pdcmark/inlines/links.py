"""
Link / image resolution pass.

Walks the inline node list pairing `LinkOpenNode`s with `LinkCloseNode`s; for each successful pair builds a `LinkGroup`.
Unresolvable openers / closers fall back to literal text.

Cf. pulldown-cmark/src/parse.rs::{LinkStack, fetch_link_type_url_title}. The algorithm is the standard one from
CommonMark Appendix A:

  - LinkOpen pushes onto a per-pass stack with an "active" flag.
  - LinkClose pops the topmost still-active opener.
  - On a successful link (not image) resolution, all earlier link-openers are deactivated (CM's "no nested links" rule).
    Images do not trigger deactivation; an image inside a link is fine.
  - Resolution order for a closer: inline → reference → collapsed → shortcut. Whichever first succeeds wins. None
    succeeded? The opener / closer revert to text.
"""
from omlish import check
from omlish import dataclasses as dc

from ..blocks.refdefs import LinkDef
from ..blocks.refdefs import RefDefs
from ..brokenlinks import BrokenLink
from ..brokenlinks import BrokenLinkResolver
from ..events import LinkType
from ..scanning.links import normalize_link_label
from .nodes import CodeNode
from .nodes import DelimNode
from .nodes import EmphasisGroup
from .nodes import HtmlNode
from .nodes import InlineNode
from .nodes import LinkCloseNode
from .nodes import LinkGroup
from .nodes import LinkOpenNode
from .nodes import TextNode


##


@dc.dataclass()
class _LinkStackEntry:
    node_index: int    # index of LinkOpenNode in the node list
    is_image: bool
    active: bool


@dc.dataclass()
class Fuel:
    """Mutable link-ref expansion budget. Pulldown-cmark/src/parse.rs::ParserInner::link_ref_expansion_limit."""

    remaining: int


def resolve_links(
        nodes: list[InlineNode],
        refdefs: RefDefs,
        fuel: Fuel,
        broken_link_resolver: BrokenLinkResolver | None,
) -> list[InlineNode]:
    stack: list[_LinkStackEntry] = []
    i = 0
    while i < len(nodes):
        node = nodes[i]
        if isinstance(node, LinkOpenNode):
            stack.append(_LinkStackEntry(node_index=i, is_image=node.is_image, active=True))
            i += 1
            continue
        if isinstance(node, LinkCloseNode):
            # Per CM Appendix A we only consider the topmost opener. If the top of stack is a deactivated link, the
            # closer fails AND the deactivated opener is dropped from the stack. (We still convert it to text below for
            # unmatched-opener cleanup.) Images remain matchable regardless of any "active" considerations.
            if not stack:
                nodes[i] = TextNode(
                    offset=(node.offset[0], node.consumed_end),
                    text=node.raw_consumed,
                )
                i += 1
                continue
            top = stack[-1]
            if not (top.active or top.is_image):
                # Disabled link on top — closer fails, pop the disabled opener AND convert it to text right now (so it
                # doesn't get stranded inside any outer group's children).
                opener = nodes[top.node_index]
                if isinstance(opener, LinkOpenNode):
                    nodes[top.node_index] = TextNode(
                        offset=opener.offset,
                        text='![' if opener.is_image else '[',
                    )
                nodes[i] = TextNode(
                    offset=(node.offset[0], node.consumed_end),
                    text=node.raw_consumed,
                )
                stack.pop()
                i += 1
                continue
            match_s = len(stack) - 1
            entry = stack[match_s]
            opener = check.isinstance(nodes[entry.node_index], LinkOpenNode)

            # Inner children = nodes strictly between opener and closer.
            children = nodes[entry.node_index + 1:i]

            # Try resolution.
            resolved = _try_resolve_link(
                close_node=node,
                children=children,
                refdefs=refdefs,
                fuel=fuel,
                broken_link_resolver=broken_link_resolver,
            )
            if resolved is not None:
                group = LinkGroup(
                    offset=(opener.offset[0], node.consumed_end),
                    is_image=entry.is_image,
                    link_type=resolved.link_type,
                    dest_url=resolved.dest_url,
                    title=resolved.title,
                    id=resolved.id,
                    children=children,
                )
                # Replace nodes[opener_node_i:closer_node_i+1] (which includes any nodes that the tokenizer left between
                # e.g. for `[foo][bar]`, the inner-`[bar]` was already consumed by the closer's scan; only the `[`
                # opener through `]` closer occupies node slots).
                nodes[entry.node_index:i + 1] = [group]
                # Stack: drop everything from match_s onward (inner openers are now inside group).
                stack = stack[:match_s]
                # If this was a link (not image), deactivate all earlier link openers.
                if not entry.is_image:
                    for e in stack:
                        if not e.is_image:
                            e.active = False
                # Continue right after the group.
                i = entry.node_index + 1
                continue

            # No resolution. For a non-image link, CM says we deactivate this opener (and earlier links) but leave its
            # `[` in the source as text. The closer (with any consumed suffix) becomes text. For an image, both opener
            # and closer just revert to text.
            nodes[i] = TextNode(
                offset=(node.offset[0], node.consumed_end),
                text=node.raw_consumed,
            )
            if entry.is_image:
                nodes[entry.node_index] = TextNode(
                    offset=opener.offset,
                    text='![',
                )
                stack.pop()
            else:
                # Convert this opener to text immediately and pop. Don't propagate deactivation to earlier link openers
                # — only successful resolutions do that.
                nodes[entry.node_index] = TextNode(
                    offset=opener.offset,
                    text='[',
                )
                stack.pop()
            i += 1
            continue
        i += 1

    # Finalize: convert any remaining placeholders to text, including those stranded inside successfully-built LinkGroup
    # children (can happen when an inner closer pairs with an outer opener over a still-present inner opener — see CM
    # example 519).
    _finalize_link_placeholders(nodes)
    return nodes


def _finalize_link_placeholders(nodes: list[InlineNode]) -> None:
    for j in range(len(nodes)):
        n = nodes[j]
        if isinstance(n, LinkOpenNode):
            nodes[j] = TextNode(
                offset=n.offset,
                text='![' if n.is_image else '[',
            )
        elif isinstance(n, LinkCloseNode):
            nodes[j] = TextNode(
                offset=(n.offset[0], n.consumed_end),
                text=n.raw_consumed,
            )
        elif isinstance(n, LinkGroup):
            _finalize_link_placeholders(n.children)


##


@dc.dataclass(frozen=True)
class _Resolved:
    link_type: LinkType
    dest_url: str
    title: str
    id: str


def _try_resolve_link(
        *,
        close_node: LinkCloseNode,
        children: list[InlineNode],
        refdefs: RefDefs,
        fuel: Fuel,
        broken_link_resolver: BrokenLinkResolver | None,
) -> _Resolved | None:
    if close_node.kind == 'inline':
        return _Resolved(
            link_type=LinkType.INLINE,
            dest_url=close_node.dest_url,
            title=close_node.title,
            id='',
        )
    if close_node.kind == 'reference':
        label = normalize_link_label(close_node.label)
        ld = _lookup_with_fuel(label, refdefs, fuel)
        if ld is not None:
            return _Resolved(LinkType.REFERENCE, ld.dest, ld.title, label)
        return _try_broken(LinkType.REFERENCE, label, close_node, broken_link_resolver)
    # 'collapsed' or 'shortcut' — label is the inner text.
    inner_label = normalize_link_label(_flatten_to_text(children))
    if not inner_label:
        return None
    ld = _lookup_with_fuel(inner_label, refdefs, fuel)
    if ld is not None:
        lt = LinkType.COLLAPSED if close_node.kind == 'collapsed' else LinkType.SHORTCUT
        return _Resolved(lt, ld.dest, ld.title, inner_label)
    lt = LinkType.COLLAPSED if close_node.kind == 'collapsed' else LinkType.SHORTCUT
    return _try_broken(lt, inner_label, close_node, broken_link_resolver)


def _lookup_with_fuel(label: str, refdefs: RefDefs, fuel: Fuel) -> LinkDef | None:
    if fuel.remaining <= 0:
        return None
    ld = refdefs.get(label)
    if ld is None:
        return None
    cost = len(ld.dest) + len(ld.title)
    if cost > fuel.remaining:
        return None
    fuel.remaining -= cost
    return ld


def _try_broken(
        link_type: LinkType,
        label: str,
        close_node: LinkCloseNode,
        broken_link_resolver: BrokenLinkResolver | None,
) -> _Resolved | None:
    if broken_link_resolver is None:
        return None
    unknown_type = _to_unknown(link_type)
    bl = BrokenLink(
        span=close_node.offset,
        link_type=unknown_type,
        reference=label,
    )
    res = broken_link_resolver(bl)
    if res is None:
        return None
    return _Resolved(unknown_type, res.dest_url, res.title, label)


def _to_unknown(link_type: LinkType) -> LinkType:
    return {
        LinkType.REFERENCE: LinkType.REFERENCE_UNKNOWN,
        LinkType.COLLAPSED: LinkType.COLLAPSED_UNKNOWN,
        LinkType.SHORTCUT: LinkType.SHORTCUT_UNKNOWN,
    }.get(link_type, link_type)


def _flatten_to_text(nodes: list[InlineNode]) -> str:
    """
    Collapse a sequence of inline nodes into a label-style string (whitespace-collapsed, case-foldable). Used to derive
    the implicit label for collapsed / shortcut refs.

    Important: this runs DURING link resolution, before emphasis has been resolved. So emphasis delimiters appear as raw
    `DelimNode`s and their literal characters must be included for the label to match what was written in the refdef
    line. Example: a refdef `[foo *bar*]: /url` registers the label as `foo *bar*`; the shortcut use `[foo *bar*]` must
    derive the same label, asterisks and all.
    """

    parts: list[str] = []
    for n in nodes:
        if isinstance(n, TextNode):
            parts.append(n.text)
        elif isinstance(n, DelimNode):
            parts.append(n.char * n.count)
        elif isinstance(n, EmphasisGroup):
            parts.append(_flatten_to_text(n.children))
        elif isinstance(n, LinkGroup):
            parts.append(_flatten_to_text(n.children))
        elif isinstance(n, (CodeNode, HtmlNode)):
            parts.append(n.text)
    return ''.join(parts)
