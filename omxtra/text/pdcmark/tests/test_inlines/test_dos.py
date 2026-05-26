"""
Adversarial input tests - the link-reference expansion-bomb that motivates pulldown's `link_ref_expansion_limit` (see
pulldown-cmark issue #844 and parse.rs::ParserInner). Without the fuel guard, an input that repeatedly references the
same large refdef can balloon output size quadratically.
"""
import time

from omlish import dataclasses as dc

from .... import pdcmark as m
from ...options import COMMONMARK
from ...rendering.html import render_html


def test_link_ref_expansion_bomb_stays_bounded():
    # `[x]: <large>` followed by N copies of `[x]` would, without fuel, produce N copies of <large> in the rendered
    # output. With fuel, expansion bails after the configured budget.
    big = 'A' * 5000
    refs = '\n[x]\n' * 200
    src = f'[x]: {big}\n{refs}'

    # Cap fuel low so we definitely exhaust.
    opts = dc.replace(COMMONMARK, link_ref_expansion_min=10_000)

    t0 = time.monotonic()
    out = render_html(m.parse(src, opts))
    elapsed = time.monotonic() - t0

    # Output size should be bounded by something like fuel + overhead.
    assert len(out) < 50_000, f'output ballooned to {len(out)} bytes - fuel guard not effective'
    # And it shouldn't take noticeable wall time on a sane impl.
    assert elapsed < 2.0, f'expansion bomb took {elapsed:.2f}s'


def test_link_ref_resolves_when_fuel_available():
    # Sanity: with default fuel the same shape but fewer refs works fine.
    src = '[x]: /url\n\n[x]\n'
    out = render_html(m.parse(src))
    assert '/url' in out
