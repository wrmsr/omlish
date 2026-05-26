from .... import pdcmark as m
from ...rendering.html import render_html


def render(src):
    return render_html(m.parse(src))


def test_paragraph():
    assert render('hello\n') == '<p>hello</p>\n'


def test_heading():
    assert render('# h1\n') == '<h1>h1</h1>\n'
    assert render('## h2\n') == '<h2>h2</h2>\n'


def test_setext_heading_h1():
    assert render('Title\n===\n') == '<h1>Title</h1>\n'


def test_setext_heading_h2():
    assert render('Title\n---\n') == '<h2>Title</h2>\n'


def test_thematic_break():
    assert render('---\n') == '<hr />\n'


def test_fenced_code():
    out = render('```\nx\n```\n')
    assert out == '<pre><code>x\n</code></pre>\n'


def test_fenced_code_with_lang():
    out = render('```python\nx = 1\n```\n')
    assert out == '<pre><code class="language-python">x = 1\n</code></pre>\n'


def test_indented_code():
    out = render('    code\n')
    assert out == '<pre><code>code\n</code></pre>\n'


def test_html_block():
    out = render('<div>\nhi\n</div>\n')
    assert out == '<div>\nhi\n</div>\n'


def test_blockquote():
    out = render('> quoted\n')
    assert out == '<blockquote>\n<p>quoted</p>\n</blockquote>\n'


def test_blockquote_paragraph_with_lazy():
    out = render('> foo\nbar\n')
    assert out == '<blockquote>\n<p>foo\nbar</p>\n</blockquote>\n'


def test_unordered_list_tight():
    out = render('- a\n- b\n')
    assert out == '<ul>\n<li>a</li>\n<li>b</li>\n</ul>\n'


def test_unordered_list_loose():
    out = render('- a\n\n- b\n')
    assert out == '<ul>\n<li>\n<p>a</p>\n</li>\n<li>\n<p>b</p>\n</li>\n</ul>\n'


def test_ordered_list_default_start_tight():
    out = render('1. a\n2. b\n')
    assert out == '<ol>\n<li>a</li>\n<li>b</li>\n</ol>\n'


def test_ordered_list_custom_start():
    out = render('42. a\n')
    assert out.startswith('<ol start="42">')


def test_nested_list():
    out = render('- a\n  - b\n')
    assert '<ul>' in out and out.count('<ul>') == 2


def test_blockquote_with_list():
    out = render('> - a\n')
    assert out == '<blockquote>\n<ul>\n<li>a</li>\n</ul>\n</blockquote>\n'


def test_text_escape():
    out = render('5 < 6\n')
    assert out == '<p>5 &lt; 6</p>\n'


def test_amp_escape():
    out = render('a & b\n')
    assert out == '<p>a &amp; b</p>\n'


def test_refdef_only_no_output():
    out = render('[foo]: /url\n')
    assert out == ''


def test_refdef_then_paragraph():
    out = render('[foo]: /url\n\nhello\n')
    assert out == '<p>hello</p>\n'


def test_multiple_blocks():
    out = render('# h\n\npara\n')
    assert out == '<h1>h</h1>\n<p>para</p>\n'
