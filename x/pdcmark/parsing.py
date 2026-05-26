"""
Oneshot `parse(text)` entry point.

Thin shim over `BlockMachine`: splits input into lines, feeds each, and finishes. Streaming consumers use
`pdcmark.streaming.StreamingParser` instead.

Honors `options.prescan_refdefs`: when True, runs a discarded first pass solely to populate the refdef table so that
links can resolve against refdefs defined later in the document. The first pass discards events; the second pass starts
with the refdefs pre-populated and emits events normally. Cf. pulldown-cmark's two-pass design, which collects refdefs
into the tree before the inline pass runs.
"""
import typing as ta

from .blocks.machine import BlockMachine
from .blocks.refdefs import RefDefs
from .events import Event
from .options import COMMONMARK
from .options import Options


##


def parse(text: str, options: Options = COMMONMARK) -> list[Event]:
    """
    Parse `text` and return a materialized list of `Event`s.

    For incremental / chunked input, use `pdcmark.StreamingParser` instead. With `options.prescan_refdefs=True`, a
    discarded first pass populates the refdef table so forward-referencing links resolve; default is False (matching
    streaming behavior).
    """

    refdefs: RefDefs | None = None
    if options.prescan_refdefs:
        refdefs = _prescan(text, options)
    bm = BlockMachine(options, refdefs=refdefs)
    events: list[Event] = []
    for line_body, line_start, line_next in _iter_lines(text):
        events.extend(bm.feed_line(line_body, line_start, line_next))
    events.extend(bm.finish(len(text)))
    return events


def _prescan(text: str, options: Options) -> RefDefs:
    """Run the BlockMachine to completion, discard the events, return the refdef table."""

    bm = BlockMachine(options)
    for line_body, line_start, line_next in _iter_lines(text):
        bm.feed_line(line_body, line_start, line_next)
    bm.finish(len(text))
    return bm.refdefs


def _iter_lines(text: str) -> ta.Iterator[tuple[str, int, int]]:
    n = len(text)
    pos = 0
    while pos < n:
        nl_pos = pos
        while nl_pos < n and text[nl_pos] != '\n' and text[nl_pos] != '\r':
            nl_pos += 1
        body = text[pos:nl_pos]
        if nl_pos < n and text[nl_pos] == '\r' and nl_pos + 1 < n and text[nl_pos + 1] == '\n':
            nl_len = 2
        elif nl_pos < n:
            nl_len = 1
        else:
            nl_len = 0
        next_off = nl_pos + nl_len
        yield body, pos, next_off
        pos = next_off
