"""
Chunked-input streaming parser.

`StreamingParser` wraps a `BlockMachine` with a line buffer. `feed(chunk)` accepts any string — chunks may break across
lines, words, or even multi-byte boundaries (since we work in `str` units). The output of each call is a `FeedOutput`
with two parts: the newly-committed events (the consumer appends these to a stable log) and the current tentative tail
(the consumer replaces its previous tentative with this one).

See docs/02_PrePlan.md and docs/00_Goals.md for the contract:
  - Committed events are immutable / append-only.
  - `committed + tentative` at any moment equals what an oracle on the prefix-seen-so-far would have produced.
  - Full-reparse equivalence: chunking has zero observable effect on the final committed stream.
"""
import copy

from ..blocks.machine import BlockMachine
from ..errors import ParserStateError
from ..events import Event
from ..options import COMMONMARK
from ..options import Options
from .output import FeedOutput


##


class StreamingParser:
    """
    Chunk-fed markdown parser. Each `feed(chunk)` returns a `FeedOutput` carrying:

      - `committed` — events newly finalized; append to your stable log.
      - `tentative` — current best-effort tail; replace your previous tentative with this one.

    Calling `feed("")` is an explicit no-op. After `finish()`, further `feed()` calls raise `ParserStateError`. For any
    chunking of input, the concatenated `committed` stream equals `pdcmark.parse(input)`.
    """

    def __init__(self, options: Options = COMMONMARK) -> None:
        super().__init__()
        self._options = options
        self._bm = BlockMachine(options)
        self._buffer = ''  # accumulated chars not yet known to be a complete line
        self._offset = 0   # absolute char offset where `_buffer` begins
        self._last_tentative: list[Event] = []
        self._terminated = False

    # Public entry points.

    def feed(self, chunk: str) -> FeedOutput:
        if self._terminated:
            raise ParserStateError('StreamingParser: feed() after finish()')
        if not chunk:
            # Empty feed — explicit no-op. The previous tentative is unchanged.
            return FeedOutput(committed=(), tentative=tuple(self._last_tentative))

        self._buffer += chunk
        committed: list[Event] = []
        self._drain_complete_lines(committed)

        # Tentative reflects current buffer + open-block state.
        self._last_tentative = self._compute_tentative()
        return FeedOutput(
            committed=tuple(committed),
            tentative=tuple(self._last_tentative),
        )

    def finish(self) -> FeedOutput:
        if self._terminated:
            return FeedOutput(committed=(), tentative=())

        committed: list[Event] = []
        # Drain any complete lines still in buffer (shouldn't happen normally, but be safe).
        self._drain_complete_lines(committed)

        # Treat any unterminated trailing buffer as the last line.
        if self._buffer:
            line_body = self._buffer
            line_start = self._offset
            next_off = line_start + len(line_body)
            committed.extend(self._bm.feed_line(line_body, line_start, next_off))
            self._offset = next_off
            self._buffer = ''

        committed.extend(self._bm.finish(self._offset))
        self._terminated = True
        self._last_tentative = []
        return FeedOutput(committed=tuple(committed), tentative=())

    # Internal.

    def _drain_complete_lines(self, committed: list[Event]) -> None:
        """
        Pull complete (newline-terminated) lines out of the buffer and feed them into the block machine. Recognizes LF
        and CRLF terminators; bare CR followed by non-`\\n` is also treated as a line break, but a CR at the very end of
        buffer is held for the next chunk in case it turns into CRLF.\
        """

        while True:
            nl_pos = self._buffer.find('\n')
            if nl_pos < 0:
                # No LF. Check for an unambiguous bare CR (one not at end of buffer).
                cr_pos = self._buffer.find('\r')
                if cr_pos < 0:
                    return
                if cr_pos == len(self._buffer) - 1:
                    # CR at end — defer; the next chunk might supply `\n` to form CRLF.
                    return
                line_body = self._buffer[:cr_pos]
                nl_len = 1
                line_start = self._offset
                next_off = line_start + len(line_body) + nl_len
                committed.extend(self._bm.feed_line(line_body, line_start, next_off))
                self._offset = next_off
                self._buffer = self._buffer[cr_pos + 1:]
                continue

            line_body = self._buffer[:nl_pos]
            if line_body.endswith('\r'):
                line_body = line_body[:-1]
                nl_len = 2  # CRLF
            else:
                nl_len = 1  # LF
            line_start = self._offset
            next_off = line_start + len(line_body) + nl_len
            committed.extend(self._bm.feed_line(line_body, line_start, next_off))
            self._offset = next_off
            self._buffer = self._buffer[nl_pos + 1:]

    def _compute_tentative(self) -> list[Event]:
        """
        Events that would be emitted if input ended right now.

        Clones the BlockMachine (deepcopy), feeds the partial trailing line if any, and finishes the clone. The clone is
        discarded; the live BlockMachine is unaffected.
        """

        if not self._buffer and not self._bm.has_open_block:
            return []
        clone = copy.deepcopy(self._bm)
        events: list[Event] = []
        if self._buffer:
            partial_start = self._offset
            partial_end = partial_start + len(self._buffer)
            events.extend(clone.feed_line(self._buffer, partial_start, partial_end))
        else:
            partial_end = self._offset
        events.extend(clone.finish(partial_end))
        return events
