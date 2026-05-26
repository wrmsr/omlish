from pdcmark.scanning.blockquotes import scan_blockquote_marker


def test_bare_marker():
    assert scan_blockquote_marker('>') == 1


def test_marker_with_space():
    assert scan_blockquote_marker('> foo') == 2


def test_marker_with_tab():
    assert scan_blockquote_marker('>\tfoo') == 2


def test_not_a_marker():
    assert scan_blockquote_marker('x') is None
    assert scan_blockquote_marker('') is None
