from pdcmark.scanning.inlinehtml import scan_inline_html


def test_open_tag_simple():
    m = scan_inline_html('<a>', 0)
    assert m is not None and m.end == 3


def test_open_tag_with_attrs():
    m = scan_inline_html('<a href="x" id=y>', 0)
    assert m is not None


def test_self_closing():
    m = scan_inline_html('<br />', 0)
    assert m is not None and m.end == 6


def test_close_tag():
    m = scan_inline_html('</a>', 0)
    assert m is not None


def test_comment():
    m = scan_inline_html('<!-- hi -->', 0)
    assert m is not None and m.end == 11


def test_comment_with_dashes_invalid():
    assert scan_inline_html('<!-- a -- b -->', 0) is None


def test_processing_instruction():
    m = scan_inline_html('<?php ?>', 0)
    assert m is not None


def test_declaration():
    m = scan_inline_html('<!DOCTYPE html>', 0)
    assert m is not None


def test_cdata():
    m = scan_inline_html('<![CDATA[ x ]]>', 0)
    assert m is not None


def test_not_html():
    assert scan_inline_html('text', 0) is None
    assert scan_inline_html('< not tag>', 0) is None
