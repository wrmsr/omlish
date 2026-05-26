"""
`FeedOutput` - return value of `StreamingParser.feed()` / `.finish()`.

See docs/02_PrePlan.md for the streaming model and invariants.
"""
import typing as ta

from omlish import dataclasses as dc

from ..events import Event


##


@dc.dataclass(frozen=True, kw_only=True)
class FeedOutput:
    """
    Events produced by one `feed()` / `finish()` call.

    - `committed` - events newly committed since the previous call. The consumer APPENDS these to its stable event log.
      Committed events never change.
    - `tentative` - the full current tentative tail: what the parser would emit if input ended right now. The consumer
      REPLACES its prior tentative list with this one. Tentative events may differ between calls; they reflect the
      in-flight state of the parser.
    """

    committed: ta.Sequence[Event]
    tentative: ta.Sequence[Event]
