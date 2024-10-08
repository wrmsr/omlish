import pytest

from ..styles import IrcTextColor
from ..styles import IrcTextStyle
from ..styles import strip_styles
from ..styles import styled


@pytest.mark.parametrize(('args', 'expected'), [
    (('test', IrcTextColor.CYAN), '\x0311test\x03'),
    (('test', IrcTextColor.CYAN, IrcTextColor.RED), '\x0311,4test\x03'),
    (('test', None, None, IrcTextStyle.BOLD), '\x02test\x0f'),
    (('test', None, None, [IrcTextStyle.BOLD, IrcTextStyle.ITALIC]), '\x02\x1dtest\x0f'),
    (('test', IrcTextColor.CYAN, IrcTextColor.RED, [IrcTextStyle.BOLD, IrcTextStyle.ITALIC]), '\x02\x1d\x0311,4test\x03\x0f'),  # noqa
], ids=['foreground', 'both_colors', 'bold', 'bold_italic', 'colors_styles'])
def test_styled(args, expected):
    assert styled(*args) == expected


@pytest.mark.parametrize(('text', 'expected'), [
    ('abc def \x0311test\x03 xyz', 'abc def test xyz'),
    ('\x0311,4blah\x03 text \x02bold', 'blah text bold'),
    ('\x0311all colors', 'all colors'),
])
def test_strip_styles(text, expected):
    assert strip_styles(text) == expected
