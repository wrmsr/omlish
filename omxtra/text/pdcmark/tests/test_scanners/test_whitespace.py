from pdcmark.scanning.whitespace import is_blank_line
from pdcmark.scanning.whitespace import scan_blank_line
from pdcmark.scanning.whitespace import scan_ch_repeat
from pdcmark.scanning.whitespace import scan_eol
from pdcmark.scanning.whitespace import scan_whitespace_no_nl


def test_scan_whitespace_no_nl():
    assert scan_whitespace_no_nl('   abc', 0) == 3
    assert scan_whitespace_no_nl('\t\t x', 0) == 3
    assert scan_whitespace_no_nl('abc', 0) == 0
    assert scan_whitespace_no_nl('a   ', 1) == 3
    # newlines do NOT count
    assert scan_whitespace_no_nl(' \nx', 0) == 1


def test_scan_ch_repeat():
    assert scan_ch_repeat('====', 0, '=') == 4
    assert scan_ch_repeat('=== abc', 0, '=') == 3
    assert scan_ch_repeat('x===', 0, '=') == 0
    assert scan_ch_repeat('x===', 1, '=') == 3


def test_scan_eol():
    assert scan_eol('', 0) == 0
    assert scan_eol('\n', 0) == 1
    assert scan_eol('\r\n', 0) == 2
    assert scan_eol('\r', 0) == 1
    assert scan_eol('\rx', 0) == 1
    assert scan_eol('abc', 0) is None
    assert scan_eol('abc\n', 3) == 1


def test_scan_blank_line():
    assert scan_blank_line('') == 0
    assert scan_blank_line('\n') == 1
    assert scan_blank_line('   \n') == 4
    assert scan_blank_line('   \r\n') == 5
    assert scan_blank_line('   x\n') is None
    assert scan_blank_line('abc\n   \n', 4) == 4  # blank line after offset


def test_is_blank_line():
    assert is_blank_line('')
    assert is_blank_line('   ')
    assert is_blank_line('\t \t')
    assert not is_blank_line('a')
    assert not is_blank_line('  a')
