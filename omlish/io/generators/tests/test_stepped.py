import typing as ta

from .... import check
from .... import lang
from ..stepped import buffer_bytes_stepped_reader_generator
from ..stepped import flatmap_stepped_generator


T = ta.TypeVar('T')


def of_equal_to(v: T) -> ta.Callable[[T], bool]:
    def inner(e):
        return e == v
    return inner


def test_fmg():
    @lang.autostart
    def f():
        for _ in range(3):
            s = check.isinstance((yield), str)
            check.none((yield s + '?'))
            check.none((yield s + '!'))
        check.none((yield ''))

    print()

    g: ta.Any = flatmap_stepped_generator(lang.identity, f())
    for s in 'abc':
        print(repr(g.send(s)))
    print()

    g = flatmap_stepped_generator(lang.identity, f(), terminate=of_equal_to('c?'))
    for s in 'abc':
        print(repr(g.send(s)))
    print()

    g = flatmap_stepped_generator(''.join, f(), terminate=of_equal_to('c?'))
    for s in 'abc':
        print(repr(g.send(s)))
    print()

    g = flatmap_stepped_generator(''.join, f(), terminate=of_equal_to(''))
    for s in 'abc':
        print(repr(g.send(s)))
    print()

    g = flatmap_stepped_generator(''.join, f(), terminate=of_equal_to('c?'))
    for s in 'abc':
        print(repr(g.send(s)))
    print()

    g = flatmap_stepped_generator(''.join, f(), terminate=of_equal_to('c?'))
    for o in lang.genmap(g, 'abc'):
        print(repr(o))
    print()


def test_buffer():
    def f():
        assert (yield 1) == b'a'
        assert (yield 2) == b'bc'
        assert (yield 1) == b'd'

    g = buffer_bytes_stepped_reader_generator(f())
    g.send(b'abcd')
