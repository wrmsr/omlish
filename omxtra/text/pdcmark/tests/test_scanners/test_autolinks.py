from ...scanning.autolinks import scan_autolink


def test_basic_uri():
    m = scan_autolink('<http://example.com>', 0)
    assert m is not None and m.target == 'http://example.com' and not m.is_email


def test_email():
    m = scan_autolink('<foo@example.com>', 0)
    assert m is not None and m.target == 'foo@example.com' and m.is_email


def test_uri_with_path():
    m = scan_autolink('<https://x.test/a/b?c=1>', 0)
    assert m is not None and not m.is_email


def test_uri_reject_whitespace():
    assert scan_autolink('<http://x .com>', 0) is None


def test_no_close_bracket():
    assert scan_autolink('<http://x.com', 0) is None


def test_not_open():
    assert scan_autolink('http://x', 0) is None


def test_not_uri_or_email():
    assert scan_autolink('<no_scheme>', 0) is None


def test_offset():
    m = scan_autolink('foo <http://x.test> bar', 4)
    assert m is not None
