from pdcmark.events import Alignment
from pdcmark.scanning.tables import line_could_be_table_row
from pdcmark.scanning.tables import parse_alignment_row
from pdcmark.scanning.tables import parse_table_row


def test_align_basic():
    assert parse_alignment_row('| --- | --- |') == (Alignment.NONE, Alignment.NONE)


def test_align_left():
    assert parse_alignment_row('| :--- | :--- |') == (Alignment.LEFT, Alignment.LEFT)


def test_align_right():
    assert parse_alignment_row('| ---: | ---: |') == (Alignment.RIGHT, Alignment.RIGHT)


def test_align_center():
    assert parse_alignment_row('| :---: | :---: |') == (Alignment.CENTER, Alignment.CENTER)


def test_align_mixed():
    assert parse_alignment_row('| :- | -: | :-: | - |') == (
        Alignment.LEFT, Alignment.RIGHT, Alignment.CENTER, Alignment.NONE)


def test_align_no_pipes():
    assert parse_alignment_row('--- | ---') == (Alignment.NONE, Alignment.NONE)


def test_align_single_column():
    assert parse_alignment_row('| --- |') == (Alignment.NONE,)


def test_align_invalid_no_dashes():
    assert parse_alignment_row('| : | : |') is None


def test_align_invalid_text():
    assert parse_alignment_row('| abc | def |') is None


def test_align_indent_4_no():
    assert parse_alignment_row('    | --- |') is None


def test_row_basic():
    assert parse_table_row('| a | b |', 2) == ['a', 'b']


def test_row_no_outer_pipes():
    assert parse_table_row('a | b', 2) == ['a', 'b']


def test_row_escaped_pipe():
    assert parse_table_row(r'| a\|b | c |', 2) == ['a|b', 'c']


def test_row_pads_missing():
    assert parse_table_row('| a |', 3) == ['a', '', '']


def test_row_truncates_extra():
    assert parse_table_row('| a | b | c |', 2) == ['a', 'b']


def test_row_strips_cell_ws():
    assert parse_table_row('|  a  |  b  |', 2) == ['a', 'b']


def test_line_could_be_table_row():
    assert line_could_be_table_row('| a |')
    assert line_could_be_table_row('a | b')
    assert not line_could_be_table_row('plain text')
    assert not line_could_be_table_row(r'escaped \|')
