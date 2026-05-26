"""
Coalesce consecutive `Text` events into one and drop empties.

The parser emits many small `Text` events because each text fragment maps to a slice of the source. Most consumers want
them merged. Cf. `pulldown-cmark/src/utils.rs::TextMergeStream` and `TextMergeWithOffset` - same semantics, plus our
`Text` events carry source offsets so we widen the span to cover the merged range.
"""
import io
import typing as ta

from ..events import Event
from ..events import Text


##


def merge_text(events: ta.Iterable[Event]) -> ta.Iterator[Event]:
    buf: io.StringIO | None = None
    span_start = 0
    span_end = 0

    for ev in events:
        if isinstance(ev, Text):
            if buf is None:
                buf = io.StringIO()
                span_start, span_end = ev.offset
            else:
                span_end = ev.offset[1]
            buf.write(ev.text)
            continue

        if buf is not None:
            merged = buf.getvalue()
            buf = None
            if merged:
                yield Text(offset=(span_start, span_end), text=merged)
        yield ev

    if buf is not None:
        merged = buf.getvalue()
        if merged:
            yield Text(offset=(span_start, span_end), text=merged)
