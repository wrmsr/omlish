from pdcmark.scanning.entities import scan_entity


def test_named():
    m = scan_entity('&copy;', 0)
    assert m is not None and m.decoded == '©' and m.end == 6


def test_decimal():
    m = scan_entity('&#35;', 0)
    assert m is not None and m.decoded == '#'


def test_hex_lower():
    m = scan_entity('&#x22;', 0)
    assert m is not None and m.decoded == '"'


def test_hex_upper():
    m = scan_entity('&#X22;', 0)
    assert m is not None and m.decoded == '"'


def test_invalid_codepoint_zero():
    m = scan_entity('&#0;', 0)
    assert m is not None and m.decoded == '�'


def test_invalid_codepoint_too_large():
    m = scan_entity('&#x123456;', 0)
    # 0x123456 > 0x10FFFF
    assert m is not None and m.decoded == '�'


def test_unknown_named_returns_none():
    assert scan_entity('&bogus;', 0) is None


def test_no_semicolon():
    assert scan_entity('&copy', 0) is None


def test_not_ampersand():
    assert scan_entity('x', 0) is None


def test_embedded_offset():
    m = scan_entity('hello &amp; world', 6)
    assert m is not None and m.decoded == '&' and m.end == 11
