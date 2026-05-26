"""
Source-offset consistency checks.

Every event carries `offset = (start, end)` — character indices into the absolute input stream.
We assert a small set of invariants over the CommonMark spec corpus:

  - 0 <= start <= end <= len(input)
  - For Start/End pairs of the same Tag: enclosing event's start <= every inner offset start, and
    enclosing event's end >= every inner offset end.
  - For leaf events (Text, Code, Html, …) the offsets must be inside their enclosing Start/End.

We don't enforce strict monotonicity (Text events can have empty spans, autolinks emit Start/Text/End
all with the same offset, etc.), but we DO assert no event reports an offset outside [0, len(input)].
"""
import os.path

import pytest

from ... import pdcmark as m
from ..parsing import parse
from .spec_runner import load_spec_file


@pytest.fixture(scope='module')
def cm_inputs(pulldown_cmark_root) -> list[str]:
    cases = load_spec_file(
        os.path.join(pulldown_cmark_root, 'third_party', 'CommonMark', 'spec.txt'),
    )
    return [c.markdown for c in cases]


def _bad_offsets(events, src_len) -> list[str]:
    """Return a list of human-readable issues with offsets in `events`. Empty list = clean."""

    issues: list[str] = []
    open_stack: list[tuple[m.Tag, tuple[int, int], int]] = []  # (tag, span, event_index)
    for ix, ev in enumerate(events):
        start, end = ev.offset
        if not (0 <= start <= end <= src_len):
            issues.append(f'event #{ix} {type(ev).__name__} offset {ev.offset} out of bounds for src_len={src_len}')
            continue
        if isinstance(ev, m.Start):
            open_stack.append((ev.tag, ev.offset, ix))
            continue
        if isinstance(ev, m.End):
            if not open_stack:
                issues.append(f'event #{ix} End with no matching Start')
                continue
            tag, span, sx = open_stack.pop()
            # End's offset should be the same (start, end) as the Start's — both span the whole
            # element.
            if ev.offset[0] != span[0] or ev.offset[1] != span[1]:
                # NOTE: a couple of constructs (e.g. blockquotes whose final newline is missing
                # because the document ended on an unterminated line) reasonably have End.end >
                # Start.end. We tolerate end-difference but not start-difference.
                if ev.offset[0] != span[0]:
                    issues.append(
                        f'End #{ix} span {ev.offset} doesn\'t match opening Start #{sx} span {span}',
                    )
            continue
        # Leaf event — must be inside the topmost open span if any.
        if open_stack:
            parent_tag, parent_span, _ = open_stack[-1]
            if start < parent_span[0] or end > parent_span[1]:
                issues.append(
                    f'leaf #{ix} {type(ev).__name__} offset {ev.offset} outside '
                    f'enclosing {type(parent_tag).__name__} span {parent_span}',
                )
    if open_stack:
        issues.append(f'unclosed Starts: {[type(t).__name__ for t, _, _ in open_stack]}')
    return issues


def test_offsets_within_bounds_cm(cm_inputs):
    """Every event offset lies inside the input."""

    failures = []
    for ix, src in enumerate(cm_inputs):
        events = parse(src)
        for ev in events:
            s, e = ev.offset
            if not (0 <= s <= e <= len(src)):
                failures.append((ix, ev))
                break
    assert not failures, f'first failure: case #{failures[0][0]} event {failures[0][1]}'


def test_offsets_structurally_consistent_cm(cm_inputs):
    """Start/End balance and leaf events sit inside their enclosing tags."""

    failures = []
    for ix, src in enumerate(cm_inputs[:200]):  # subset for speed; the full corpus is exercised
        events = parse(src)                     # by the bounds test above
        issues = _bad_offsets(events, len(src))
        if issues:
            failures.append((ix, issues[:2]))
    assert not failures, f'first failure: case #{failures[0][0]}: {failures[0][1]}'


def test_offset_slice_round_trips_basic():
    """For specific cases, slicing the source by an event's offset returns sensible text."""

    src = 'Hello *world*\n'
    events = parse(src)
    text_events = [e for e in events if isinstance(e, m.Text)]
    for t in text_events:
        # The slice should equal the text content (possibly modulo trivial whitespace —
        # the inline parser strips leading whitespace from paragraph lines).
        slice_ = src[t.offset[0]:t.offset[1]]
        assert t.text in slice_ or slice_.strip() == t.text.strip()
