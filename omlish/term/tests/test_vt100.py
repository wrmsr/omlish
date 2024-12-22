from ..vt100 import Vt100Terminal


def test_vt100():
    term = Vt100Terminal(rows=16, cols=40)

    for b in '\x1b[31mHello\x1b[1m world\x1b[0m\nLine2\x1b[2JAfter clear':
        term.parse_byte(b)

    for line in term.get_screen_as_strings():
        print(repr(line))
