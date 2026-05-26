from pdcmark.scanning.links import normalize_link_label
from pdcmark.scanning.links import scan_link_destination
from pdcmark.scanning.links import scan_link_label
from pdcmark.scanning.links import scan_link_title


def test_label_basic():
    m = scan_link_label('[foo]: x', 0)
    assert m is not None and m.end == 5 and m.raw == 'foo'


def test_label_rejects_nested_open_bracket():
    assert scan_link_label('[foo[bar]', 0) is None


def test_label_rejects_only_whitespace():
    assert scan_link_label('[   ]', 0) is None


def test_label_backslash_escape():
    m = scan_link_label(r'[foo\]]', 0)
    assert m is not None and m.end == 7 and m.raw == r'foo\]'


def test_label_unterminated_returns_none():
    assert scan_link_label('[foo', 0) is None


def test_label_normalization_collapses_and_casefolds():
    assert normalize_link_label('  FOO  bar\nbaz\t  ') == 'foo bar baz'
    assert normalize_link_label('ß') == 'ss'  # unicode casefold


def test_dest_angle_bracketed():
    m = scan_link_destination('<http://x>', 0)
    assert m is not None and m.dest == 'http://x' and m.end == 10


def test_dest_bare():
    m = scan_link_destination('http://x rest', 0)
    assert m is not None and m.dest == 'http://x' and m.end == 8


def test_dest_balanced_parens_ok():
    m = scan_link_destination('foo(bar)baz', 0)
    assert m is not None and m.dest == 'foo(bar)baz'


def test_dest_unbalanced_parens_no():
    assert scan_link_destination('foo(bar', 0) is None


def test_dest_empty_no():
    assert scan_link_destination('', 0) is None


def test_dest_angle_rejects_control_chars():
    assert scan_link_destination('<http://x\ny>', 0) is None


def test_title_double_quoted():
    m = scan_link_title('"hello"', 0)
    assert m is not None and m.title == 'hello' and m.end == 7


def test_title_single_quoted():
    m = scan_link_title("'hi'", 0)
    assert m is not None and m.title == 'hi'


def test_title_parens():
    m = scan_link_title('(hi)', 0)
    assert m is not None and m.title == 'hi'


def test_title_nested_paren_in_parens_invalid():
    assert scan_link_title('(a(b)', 0) is None


def test_title_unterminated_returns_none():
    assert scan_link_title('"unterminated', 0) is None
