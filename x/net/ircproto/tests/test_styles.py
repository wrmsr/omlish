import pytest

from ..styles import styled, IrcTextColor, IrcTextStyle, strip_styles


@pytest.mark.parametrize('args, expected', [
    (('test', IrcTextColor.cyan), '\x0311test\x03'),
    (('test', IrcTextColor.cyan, IrcTextColor.red), '\x0311,4test\x03'),
    (('test', None, None, IrcTextStyle.bold), '\x02test\x0f'),
    (('test', None, None, [IrcTextStyle.bold, IrcTextStyle.italic]), '\x02\x1dtest\x0f'),
    (('test', IrcTextColor.cyan, IrcTextColor.red, [IrcTextStyle.bold, IrcTextStyle.italic]),
     '\x02\x1d\x0311,4test\x03\x0f')
], ids=['foreground', 'both_colors', 'bold', 'bold_italic', 'colors_styles'])
def test_styled(args, expected):
    assert styled(*args) == expected


@pytest.mark.parametrize('text, expected', [
    ('abc def \x0311test\x03 xyz', 'abc def test xyz'),
    ('\x0311,4blah\x03 text \x02bold', 'blah text bold'),
    ('\x0311all colors', 'all colors')
])
def test_strip_styles(text, expected):
    assert strip_styles(text) == expected
