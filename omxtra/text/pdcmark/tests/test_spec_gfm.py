"""
Integration tests against the GFM-extension spec fixtures (vendored under the pulldown-cmark submodule's
third_party/GitHub/). Tables / strikethrough / tasklists are required to be enabled via the GFM preset; without enabling
the extensions these tests are not meaningful.
"""
import os.path

import pytest

from ..options import GFM
from ..parsing import parse
from ..rendering.html import render_html
from .spec_runner import SpecCase
from .spec_runner import load_spec_file


def _gfm_paths(pulldown_cmark_root: str) -> dict[str, str]:
    base = os.path.join(pulldown_cmark_root, 'third_party', 'GitHub')
    return {
        'gfm_strikethrough.txt': os.path.join(base, 'gfm_strikethrough.txt'),
        'gfm_table.txt': os.path.join(base, 'gfm_table.txt'),
        'gfm_tasklist.txt': os.path.join(base, 'gfm_tasklist.txt'),
    }


@pytest.fixture(scope='module')
def gfm_caseses(pulldown_cmark_root) -> dict[str, list[SpecCase]]:
    return {name: load_spec_file(p) for name, p in _gfm_paths(pulldown_cmark_root).items()}


def _passes(c: SpecCase) -> bool:
    try:
        return render_html(parse(c.markdown, GFM)) == c.expected_html
    except Exception:  # noqa
        return False


_GFM_FLOORS = {
    'gfm_strikethrough.txt': 3,
    'gfm_table.txt': 8,
    'gfm_tasklist.txt': 2,
}


@pytest.mark.parametrize('name', list(_GFM_FLOORS))
def test_gfm_file_meets_floor(gfm_caseses, name):
    cases = gfm_caseses[name]
    passes = sum(1 for c in cases if _passes(c))
    assert passes >= _GFM_FLOORS[name], (
        f'{name}: {passes}/{len(cases)} below floor {_GFM_FLOORS[name]}'
    )
