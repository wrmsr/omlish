from pdcmark.scanning.lines import LineStart


def test_scan_space_simple():
    ls = LineStart('    abc')
    assert ls.scan_space(4) is True
    assert ls.position == 4
    assert ls.remaining() == 'abc'


def test_scan_space_partial():
    ls = LineStart('  abc')
    assert ls.scan_space(4) is False
    assert ls.position == 2


def test_scan_space_upto():
    ls = LineStart('  abc')
    consumed = ls.scan_space_upto(4)
    assert consumed == 2
    assert ls.position == 2


def test_tab_expands_to_stop_of_4():
    # A tab at column 0 gives 4 columns; scan_space(4) should consume it.
    ls = LineStart('\tabc')
    assert ls.scan_space(4) is True
    assert ls.position == 1
    assert ls.remaining() == 'abc'
    assert ls.tab_carry == 0


def test_tab_partial_consumption_carries():
    # scan_space(2) on a tab consumes 2 of the 4 columns; the other 2 carry.
    ls = LineStart('\tabc')
    assert ls.scan_space(2) is True
    assert ls.tab_carry == 2
    # next scan draws from the carry first
    assert ls.scan_space(2) is True
    assert ls.tab_carry == 0
    assert ls.remaining() == 'abc'


def test_tab_advance_relative_to_position():
    # Two spaces then tab: tab advances to column 4, contributing 2 columns.
    ls = LineStart('  \tabc')
    assert ls.scan_space(4) is True
    assert ls.position == 3
    assert ls.remaining() == 'abc'


def test_scan_all_space():
    ls = LineStart('   \tabc')
    ls.scan_all_space()
    assert ls.position == 4
    assert ls.remaining() == 'abc'


def test_scan_ch():
    ls = LineStart('> blockquote')
    assert ls.scan_ch('>') is True
    assert ls.position == 1
    assert ls.scan_ch('>') is False  # next char is space
    assert ls.scan_space(1) is True
    assert ls.remaining() == 'blockquote'


def test_is_at_eol():
    ls = LineStart('abc')
    assert not ls.is_at_eol()
    ls.scan_space(3)  # doesn't move; not a space
    ls = LineStart('')
    assert ls.is_at_eol()
    ls = LineStart('\n')
    assert ls.is_at_eol()


def test_clone_and_restore():
    ls = LineStart('  > foo')
    ls.scan_space(2)
    saved = ls.clone()
    ls.scan_ch('>')
    ls.scan_space(1)
    assert ls.remaining() == 'foo'
    ls.restore(saved)
    assert ls.remaining() == '> foo'
    assert ls.position == 2
