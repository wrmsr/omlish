from ...scanning.hrule import scan_hrule


def test_simple_three_dashes():
    assert scan_hrule('---')
    assert scan_hrule('***')
    assert scan_hrule('___')


def test_more_than_three():
    assert scan_hrule('----------')


def test_spaces_between_ok():
    assert scan_hrule(' - - -')
    assert scan_hrule(' -  -    -  ')


def test_tabs_between_ok():
    assert scan_hrule('-\t-\t-')


def test_indent_up_to_3():
    assert scan_hrule('   ---')


def test_four_space_indent_no():
    assert not scan_hrule('    ---')


def test_mixed_chars_no():
    assert not scan_hrule('-_-')
    assert not scan_hrule('***-')


def test_under_three_no():
    assert not scan_hrule('--')
    assert not scan_hrule('-')


def test_other_chars_no():
    assert not scan_hrule('---a')
    assert not scan_hrule('a---')
