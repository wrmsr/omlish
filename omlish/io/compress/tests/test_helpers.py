import typing as ta

from .... import check
from .... import lang
from .helpers import flatmap_generator_writer
from .helpers import join_str


def test_fmg():
    @lang.autostart
    def f():
        for _ in range(3):
            s = check.isinstance((yield), str)
            check.none((yield s + '?'))
            check.none((yield s + '!'))
        check.none((yield ''))

    print()

    g: ta.Any = flatmap_generator_writer(lang.identity, f())
    for s in 'abc':
        print(repr(g.send(s)))
    print()

    g = flatmap_generator_writer(lang.identity, f(), terminator=lang.just('c?'))
    for s in 'abc':
        print(repr(g.send(s)))
    print()

    g = flatmap_generator_writer(''.join, f(), terminator=lang.just('c?'))
    for s in 'abc':
        print(repr(g.send(s)))
    print()

    g = flatmap_generator_writer(join_str, f(), terminator=lang.just(''))
    for s in 'abc':
        print(repr(g.send(s)))
    print()

    g = flatmap_generator_writer(join_str, f(), terminator=lang.just('c?'))
    for s in 'abc':
        print(repr(g.send(s)))
    print()

    g = flatmap_generator_writer(join_str, f(), terminator=lang.just('c?'))
    for o in lang.genmap(g, 'abc'):
        print(repr(o))
    print()
