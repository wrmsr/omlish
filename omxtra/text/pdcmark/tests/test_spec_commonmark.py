# ruff: noqa: RUF003
"""
Integration tests against the upstream CommonMark spec.txt (vendored under the pulldown-cmark submodule's
third_party/CommonMark/).
"""
import os.path

import pytest

from omlish import dataclasses as dc

from ... import pdcmark as m
from ..options import COMMONMARK
from ..rendering.html import render_html
from .spec_runner import SpecCase
from .spec_runner import load_spec_file


def _spec_path(pulldown_cmark_root: str) -> str:
    return os.path.join(pulldown_cmark_root, 'third_party', 'CommonMark', 'spec.txt')


@pytest.fixture(scope='module')
def cm_cases(pulldown_cmark_root) -> list[SpecCase]:
    return load_spec_file(_spec_path(pulldown_cmark_root))


def _render(md: str) -> str:
    return render_html(m.parse(md))


def _passes(case: SpecCase) -> bool:
    try:
        return _render(case.markdown) == case.expected_html
    except Exception:  # noqa
        return False


# Baseline


# Floor for the current milestone. Bump as later milestones land. A *drop* is a regression.
#   M1 (block-only):                          196/572
#   M2 (inline core, no links):               365/572
#   M3 (links/images, default mode):          424/572
#   M3 (links/images, prescan_refdefs=True):  468/572
#   M4 (GFM tables/strikethrough/tasklist):   429/572 / 473/572
#   M5 (tight-list rendering):                459/572 / 503/572
_BASELINE_FLOOR_DEFAULT = 459
_BASELINE_FLOOR_PRESCAN = 503


def test_cm_spec_pass_count_meets_baseline_default(cm_cases):
    passes = sum(1 for c in cm_cases if _passes(c))
    assert passes >= _BASELINE_FLOOR_DEFAULT, (
        f'Default-mode spec pass count {passes}/{len(cm_cases)} below floor {_BASELINE_FLOOR_DEFAULT}'
    )


def test_cm_spec_pass_count_meets_baseline_prescan(cm_cases):
    pre_opts = dc.replace(COMMONMARK, prescan_refdefs=True)

    def passes_with_prescan(c):
        try:
            return render_html(m.parse(c.markdown, pre_opts)) == c.expected_html
        except Exception:  # noqa
            return False

    passes = sum(1 for c in cm_cases if passes_with_prescan(c))
    assert passes >= _BASELINE_FLOOR_PRESCAN, (
        f'Prescan-mode spec pass count {passes}/{len(cm_cases)} below floor {_BASELINE_FLOOR_PRESCAN}'
    )


# Sections expected to be 100% with the M1 feature set


_STRICT_SECTIONS = (
    'Thematic breaks',
    'Blank lines',
    'Soft line breaks',
    'Textual content',
    'Paragraphs',        # M2: hard-break section now covered.
    'Inlines',           # M2: single-case section, passes once inlines work.
    'Autolinks',         # M3: all 19/19 cases passing.
    'Precedence',        # M5: 1/1 once inline parser + lists agree.
)


@pytest.mark.parametrize('section', _STRICT_SECTIONS)
def test_cm_section_full_pass(cm_cases, section):
    section_cases = [c for c in cm_cases if c.section == section]
    assert section_cases, f'no cases found for section {section!r}'
    failures = [c.index for c in section_cases if not _passes(c)]
    assert not failures, f'Failures in section {section!r}: case indices {failures}'


# Curated cases covering the key block constructs


# A small set of CM spec case indices that exercise specific M1 features and must pass. If any fails, something specific
# has regressed.
_CURATED_CASE_INDICES = (
    # Numbers reference upstream CM 0.30 spec.txt indices. Cases listed here are exact-match smoke tests covering
    # features we explicitly want green on each milestone.
    # M1 — block-level:
    1,    # tab in indented code
    43,   # thematic break (* / - / _)
    69,   # HTML block - <table>
    139,  # plain paragraph
    147,  # paragraph with leading blank lines
    148,  # blockquote with ATX heading and paragraph
    568,  # soft line break
    570,  # textual content with punctuation
    # M2 — inline core:
    13,   # backslash-escape of various ASCII punctuation
    248,  # simple code span: `foo`
    249,  # code span trimming: `` foo ` bar ``
    270,  # *foo bar*
    273,  # `* a *` — non-breaking-space flanking
    514,  # autolink URI
    515,  # autolink URI with query
    533,  # raw inline HTML series
    553,  # hard break via trailing spaces
    # M3 — links / images (default mode, no prescan needed for these):
    402,  # inline link `[link](/uri "title")`
    403,  # inline link no title
    404,  # inline link with empty text
    492,  # inline image
    # M4 — GFM extensions are tested in test_spec_gfm.py.
    # M5 — tight-list rendering:
    177,  # tight list — `-    one\n\n     two`
    221,  # mixed bullet markers → multiple tight lists
)


@pytest.mark.parametrize('idx', _CURATED_CASE_INDICES)
def test_cm_curated_case(cm_cases, idx):
    case = next((c for c in cm_cases if c.index == idx), None)
    assert case is not None, f'case index {idx} not found in CM spec'
    actual = _render(case.markdown)
    assert actual == case.expected_html, (
        f'\n'
        f'INPUT:\n'
        f'{case.markdown!r}\n'
        f'EXPECTED:\n'
        f'{case.expected_html}\n'
        f'ACTUAL:\n'
        f'{actual}'
    )
