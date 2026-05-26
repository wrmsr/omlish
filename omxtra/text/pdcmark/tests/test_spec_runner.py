import dataclasses as dc
import os.path

import pytest

from .spec_runner import SpecCase
from .spec_runner import load_spec_file
from .spec_runner import parse_spec_text


SAMPLE = """
Section One
===========

```````````````````````````````` example
# heading
.
<h1>heading</h1>
````````````````````````````````

```````````````````````````````` DISABLED example
broken
.
<p>broken</p>
````````````````````````````````


## Sub-section

```````````````````````````````` example
\tindented
.
<pre><code>indented
</code></pre>
````````````````````````````````
"""


def test_parses_inline_sample():
    cases = parse_spec_text(SAMPLE, file='sample.txt')
    assert [c.index for c in cases] == [1, 2, 3]
    assert [c.disabled for c in cases] == [False, True, False]
    assert cases[0].section == 'Section One'
    assert cases[2].section == 'Sub-section'
    assert cases[0].markdown == '# heading\n'
    assert cases[0].expected_html == '<h1>heading</h1>\n'


def test_decodes_tab_arrows():
    text = (
        '```````````````````````````````` example\n'
        '→indented\n'
        '.\n'
        '<pre><code>→indented\n'
        '</code></pre>\n'
        '````````````````````````````````\n'
    )
    cases = parse_spec_text(text, file='x.txt')
    assert cases[0].markdown == '\tindented\n'
    assert cases[0].expected_html == '<pre><code>\tindented\n</code></pre>\n'


def test_skips_non_example_fences():
    text = (
        '# title\n\n'
        '```\n'
        'non-example fence inside prose\n'
        '```\n\n'
        '```````````````````````````````` example\n'
        'hi\n'
        '.\n'
        '<p>hi</p>\n'
        '````````````````````````````````\n'
    )
    cases = parse_spec_text(text, file='x.txt')
    assert len(cases) == 1
    assert cases[0].markdown == 'hi\n'


@pytest.fixture
def upstream_files(pulldown_cmark_root):
    return [
        os.path.join(pulldown_cmark_root, 'third_party', 'CommonMark', 'spec.txt'),
        os.path.join(pulldown_cmark_root, 'specs', 'table.txt'),
        os.path.join(pulldown_cmark_root, 'third_party', 'GitHub', 'gfm_strikethrough.txt'),
        os.path.join(pulldown_cmark_root, 'third_party', 'GitHub', 'gfm_tasklist.txt'),
    ]


def test_loads_upstream_fixtures(upstream_files):
    # Sanity: every advertised fixture parses without error and has a reasonable number of cases.
    counts = {}
    for path in upstream_files:
        cases = load_spec_file(path)
        counts[os.path.basename(path)] = len(cases)
    # Upstream CommonMark spec has many hundreds; the GFM ones have a few each.
    assert counts['spec.txt'] > 500
    assert counts['table.txt'] > 10
    assert counts['gfm_strikethrough.txt'] >= 1
    assert counts['gfm_tasklist.txt'] >= 1


def test_speccase_is_frozen():
    c = SpecCase(file='x', index=1, section='', line=1, markdown='', expected_html='')
    with pytest.raises(dc.FrozenInstanceError):
        c.index = 2  # type: ignore[misc]
