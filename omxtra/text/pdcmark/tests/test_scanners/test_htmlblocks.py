from ...scanning.htmlblocks import html_block_close_on_line
from ...scanning.htmlblocks import html_block_closes_on_blank_line
from ...scanning.htmlblocks import scan_html_block_start


def test_type_1_script():
    m = scan_html_block_start('<script>')
    assert m is not None and m.type == 1


def test_type_1_with_attrs():
    m = scan_html_block_start('<pre class="x">')
    assert m is not None and m.type == 1


def test_type_1_case_insensitive():
    m = scan_html_block_start('<STYLE>')
    assert m is not None and m.type == 1


def test_type_2_comment_open():
    m = scan_html_block_start('<!-- a comment')
    assert m is not None and m.type == 2


def test_type_3_processing_instruction():
    m = scan_html_block_start('<?php echo')
    assert m is not None and m.type == 3


def test_type_4_declaration():
    m = scan_html_block_start('<!DOCTYPE html>')
    assert m is not None and m.type == 4


def test_type_5_cdata():
    m = scan_html_block_start('<![CDATA[stuff')
    assert m is not None and m.type == 5


def test_type_6_open_paragraph():
    m = scan_html_block_start('<div>')
    assert m is not None and m.type == 6


def test_type_6_close_form():
    m = scan_html_block_start('</section>')
    assert m is not None and m.type == 6


def test_type_6_with_selfclose():
    m = scan_html_block_start('<hr/>')
    assert m is not None and m.type == 6


def test_type_7_recognized():
    m = scan_html_block_start('<span>')
    assert m is not None and m.type == 7 and not m.can_interrupt_paragraph


def test_not_html_block_when_no_lt():
    assert scan_html_block_start('text') is None


def test_close_on_line_type_1():
    assert html_block_close_on_line(1, 'foo </pre> bar')
    assert html_block_close_on_line(1, '</textarea>')
    assert not html_block_close_on_line(1, 'no close here')


def test_close_on_line_type_2():
    assert html_block_close_on_line(2, 'comment --> end')
    assert not html_block_close_on_line(2, 'comment continues')


def test_close_on_line_type_3():
    assert html_block_close_on_line(3, '?>')


def test_close_on_line_type_4():
    assert html_block_close_on_line(4, '... >')


def test_close_on_line_type_5():
    assert html_block_close_on_line(5, '... ]]> ...')


def test_close_on_blank_for_6_7():
    assert html_block_closes_on_blank_line(6)
    assert html_block_closes_on_blank_line(7)
    assert not html_block_closes_on_blank_line(1)
