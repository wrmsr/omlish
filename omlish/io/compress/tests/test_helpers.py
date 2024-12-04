import typing as ta

from .... import check
from .... import lang
from .helpers import flatmap_stepped_generator
from .helpers import join_str


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

    g = flatmap_stepped_generator(join_str, f(), terminate=of_equal_to(''))
    for s in 'abc':
        print(repr(g.send(s)))
    print()

    g = flatmap_stepped_generator(join_str, f(), terminate=of_equal_to('c?'))
    for s in 'abc':
        print(repr(g.send(s)))
    print()

    g = flatmap_stepped_generator(join_str, f(), terminate=of_equal_to('c?'))
    for o in lang.genmap(g, 'abc'):
        print(repr(o))
    print()
