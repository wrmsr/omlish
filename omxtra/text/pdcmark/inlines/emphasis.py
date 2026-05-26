"""
Emphasis / strong delimiter-run resolution.

Direct port of the CommonMark Appendix A algorithm. The tokenizer produces a flat node list with `DelimNode` entries for
each emphasis-marker run. We walk those entries in order, maintaining a "delimiter stack" of openers. When we encounter
a closer we look back through the stack for a compatible opener, applying the spec's mod-3 rule, and wrap matched pairs
into `EmphasisGroup`s. Anything left unpaired at the end falls back to plain text.

Cf. pulldown-cmark/src/parse.rs::{handle_emphasis_and_hard_break, InlineStack} - same algorithm. The pulldown version
operates on its block tree in place; we operate on a fresh list.
"""
from omlish import check

from .nodes import DelimNode
from .nodes import EmphasisGroup
from .nodes import InlineNode
from .nodes import TextNode


##


def resolve_emphasis(nodes: list[InlineNode]) -> list[InlineNode]:
    """
    Resolve emphasis delimiters in `nodes` in place and return the (possibly shorter) list.

    Walks the node list left-to-right. When a closing delimiter is encountered, scans back through the delimiter stack
    for the nearest valid opener of the same char; if found, the span between is wrapped into an `EmphasisGroup`. The
    closer may match multiple openers (e.g. `***foo***` is processed in two passes, strong then emphasis).

    After the walk, any leftover `DelimNode`s - at the top level or inside groups - are converted to `TextNode`s.
    """

    delim_stack: list[int] = []
    i = 0
    while i < len(nodes):
        node = nodes[i]
        if not isinstance(node, DelimNode):
            i += 1
            continue

        if node.can_close:
            match_s = _find_matching_opener(nodes, delim_stack, node)
            if match_s is not None:
                opener_i = delim_stack[match_s]
                opener = check.isinstance(nodes[opener_i], DelimNode)

                # GFM strikethrough: `~` and `~~` both produce <del>; longer runs (`~~~+`) don't pair at all. Equivalent
                # to the GFM "tilde must be ≤ 2 chars" rule.
                if node.char == '~':
                    if opener.count > 2 or node.count > 2:
                        if node.can_open:
                            delim_stack.append(i)
                        i += 1
                        continue
                    consume = min(opener.count, node.count)
                    kind = 'strikethrough'
                else:
                    consume = 2 if min(opener.count, node.count) >= 2 else 1
                    kind = 'strong' if consume == 2 else 'emphasis'

                # Build the group: children are everything strictly between opener and closer.
                children = nodes[opener_i + 1:i]
                group = EmphasisGroup(
                    offset=(opener.offset[1] - consume, node.offset[0] + consume),
                    kind=kind,
                    children=children,
                )

                # Update opener / closer counts (mutating frozen-by-convention but actually mutable DelimNodes; they're
                # internal IR not events).
                new_opener_count = opener.count - consume
                new_closer_count = node.count - consume
                if new_opener_count > 0:
                    opener.count = new_opener_count
                    opener.offset = (opener.offset[0], opener.offset[1] - consume)
                if new_closer_count > 0:
                    node.count = new_closer_count
                    node.offset = (node.offset[0] + consume, node.offset[1])

                # Splice: replace nodes[opener_i:i+1] with [opener?, group, closer?].
                replacement: list[InlineNode] = []
                if new_opener_count > 0:
                    replacement.append(opener)
                replacement.append(group)
                if new_closer_count > 0:
                    replacement.append(node)
                nodes[opener_i:i + 1] = replacement

                # Update delim_stack: opener may or may not remain.
                if new_opener_count > 0:
                    delim_stack = delim_stack[:match_s + 1]
                else:
                    delim_stack = delim_stack[:match_s]

                # Position update: if closer remains, re-try matching at its new position.
                group_offset_in_nodes = opener_i + (1 if new_opener_count > 0 else 0)
                if new_closer_count > 0:
                    i = group_offset_in_nodes + 1
                    continue
                i = group_offset_in_nodes + 1
                continue

        if node.can_open:
            delim_stack.append(i)
        i += 1

    _finalize_remaining(nodes)
    return nodes


##


def _find_matching_opener(
        nodes: list[InlineNode],
        delim_stack: list[int],
        closer: DelimNode,
) -> int | None:
    for s_idx in reversed(range(len(delim_stack))):
        opener_i = delim_stack[s_idx]
        opener = nodes[opener_i]
        if not isinstance(opener, DelimNode):
            continue  # stale entry - was rewritten by a prior pair
        if opener.char != closer.char:
            continue
        if not opener.can_open:
            continue
        if _mod3_blocked(opener, closer):
            continue
        return s_idx
    return None


def _mod3_blocked(opener: DelimNode, closer: DelimNode) -> bool:
    # CM §6.4 mod-3 rule. Only applies when at least one of the two runs is "both" (left- and right-flanking
    # simultaneously).
    if not (opener.can_close or closer.can_open):
        return False
    if (opener.count + closer.count) % 3 != 0:
        return False
    if opener.count % 3 == 0 and closer.count % 3 == 0:
        return False
    return True


def _finalize_remaining(nodes: list[InlineNode]) -> None:
    for i in range(len(nodes)):
        n = nodes[i]
        if isinstance(n, DelimNode):
            nodes[i] = TextNode(offset=n.offset, text=n.char * n.count)
        elif isinstance(n, EmphasisGroup):
            _finalize_remaining(n.children)
