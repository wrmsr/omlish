from ...scanning.setext import scan_setext_underline


def test_basic_h1():
    assert scan_setext_underline('===') == 1
    assert scan_setext_underline('=') == 1
    assert scan_setext_underline('========') == 1


def test_basic_h2():
    assert scan_setext_underline('---') == 2
    assert scan_setext_underline('-') == 2


def test_indented_up_to_3():
    assert scan_setext_underline('   ===') == 1
    assert scan_setext_underline('   ---') == 2


def test_four_space_indent_is_not_underline():
    assert scan_setext_underline('    ===') is None


def test_trailing_whitespace_ok():
    assert scan_setext_underline('===   ') == 1
    assert scan_setext_underline('---\t') == 2


def test_other_chars_not_allowed_after():
    assert scan_setext_underline('=== foo') is None
    assert scan_setext_underline('=-=') is None


def test_mixed_chars_not_allowed():
    assert scan_setext_underline('=-') is None


def test_empty_line_not_underline():
    assert scan_setext_underline('') is None
    assert scan_setext_underline('   ') is None
