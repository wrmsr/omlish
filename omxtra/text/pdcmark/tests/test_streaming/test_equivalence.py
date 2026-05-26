"""
Full-reparse equivalence — the load-bearing invariant from docs/00_Goals.md:

  > Feeding the entire input in one feed() followed by finish() produces a committed stream
  > identical to feeding it in N arbitrary chunks followed by finish(). The consumer never
  > needs a "safety reparse at end" pass.

We verify this over the entire upstream CommonMark spec corpus and the GFM-extension corpora, under several chunking
strategies — single-char, fixed-size, random, line-boundary, etc.
"""
import os.path
import random

import pytest

from ...options import COMMONMARK
from ...options import GFM
from ...parsing import parse
from ...streaming.parser import StreamingParser
from ...tests.spec_runner import load_spec_file


# Chunking strategies — each takes a str and yields a sequence of chunks whose concatenation is the original.


def chunk_whole(s: str) -> list[str]:
    return [s]


def chunk_each_char(s: str) -> list[str]:
    return list(s)


def chunk_fixed(n: int):
    def f(s: str) -> list[str]:
        return [s[i:i + n] for i in range(0, len(s), n)] or ['']
    return f


def chunk_by_lines(s: str) -> list[str]:
    return s.splitlines(keepends=True) or ['']


def chunk_random(seed: int, min_size: int = 1, max_size: int = 16):
    """Deterministic random chunker (per `seed`)."""

    def f(s: str) -> list[str]:
        rng = random.Random(seed)
        out = []
        i = 0
        while i < len(s):
            n = rng.randint(min_size, max_size)
            out.append(s[i:i + n])
            i += n
        return out or ['']
    return f


_STRATEGIES = [
    ('whole', chunk_whole),
    ('each-char', chunk_each_char),
    ('fixed-1', chunk_fixed(1)),
    ('fixed-3', chunk_fixed(3)),
    ('fixed-32', chunk_fixed(32)),
    ('by-lines', chunk_by_lines),
    ('random-7', chunk_random(7)),
    ('random-42', chunk_random(42)),
]


def _stream(text: str, strategy, options=COMMONMARK):
    sp = StreamingParser(options)
    committed: list = []
    for chunk in strategy(text):
        out = sp.feed(chunk)
        committed.extend(out.committed)
    out = sp.finish()
    committed.extend(out.committed)
    return committed


@pytest.fixture(scope='module')
def cm_corpus(pulldown_cmark_root) -> list[str]:
    cases = load_spec_file(os.path.join(pulldown_cmark_root, 'third_party', 'CommonMark', 'spec.txt'))
    return [c.markdown for c in cases]


@pytest.fixture(scope='module')
def gfm_corpus(pulldown_cmark_root) -> list[str]:
    base = os.path.join(pulldown_cmark_root, 'third_party', 'GitHub')
    out: list[str] = []
    for f in ('gfm_strikethrough.txt', 'gfm_table.txt', 'gfm_tasklist.txt'):
        out.extend(c.markdown for c in load_spec_file(os.path.join(base, f)))
    return out


@pytest.mark.parametrize(('name', 'strategy'), _STRATEGIES)
def test_chunking_equivalence_cm(cm_corpus, name, strategy):
    """For each chunking strategy, streamed committed == oneshot parse for every CM case."""

    mismatches = []
    for ix, src in enumerate(cm_corpus):
        expected = parse(src)
        actual = _stream(src, strategy)
        if actual != expected:
            mismatches.append(ix)
    assert not mismatches, (
        f'Chunking strategy {name!r}: {len(mismatches)} CM cases diverge from oneshot. '
        f'First few: {mismatches[:5]}'
    )


@pytest.mark.parametrize(('name', 'strategy'), _STRATEGIES)
def test_chunking_equivalence_gfm(gfm_corpus, name, strategy):
    """Same equivalence under the GFM preset."""

    mismatches = []
    for ix, src in enumerate(gfm_corpus):
        expected = parse(src, GFM)
        actual = _stream(src, strategy, options=GFM)
        if actual != expected:
            mismatches.append(ix)
    assert not mismatches, (
        f'Chunking strategy {name!r}: {len(mismatches)} GFM cases diverge from oneshot. '
        f'First few: {mismatches[:5]}'
    )


def test_chunk_at_every_offset_smoke():
    """
    Spot-check: for a small fixture, every possible single-split point produces equivalent streamed and oneshot results.
    """

    src = '# Heading\n\nA paragraph with *emphasis*.\n\n- item one\n- item two\n'
    expected = parse(src)
    for i in range(len(src) + 1):
        sp = StreamingParser()
        committed: list = []
        for chunk in (src[:i], src[i:]):
            if chunk:
                committed.extend(sp.feed(chunk).committed)
        committed.extend(sp.finish().committed)
        assert committed == expected, f'split at {i} diverges'
