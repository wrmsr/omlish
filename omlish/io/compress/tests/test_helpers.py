import typing as ta

from .... import check
from .... import lang
from .helpers import flatmap_generator_writer
from .helpers import join_str


I = ta.TypeVar('I')
O = ta.TypeVar('O')
R = ta.TypeVar('R')


class GeneratorMappedIterator(ta.Generic[O, I, R]):
    def __init__(self, g: ta.Generator[O, I, R], it: ta.Iterator[I]) -> None:
        super().__init__()

        self._g = g
        self._it = it
        self._value: lang.Maybe[R] = lang.empty()

    @property
    def g(self) -> ta.Generator[O, I, R]:
        return self._g

    @property
    def it(self) -> ta.Iterator[I]:
        return self._it

    @property
    def value(self) -> lang.Maybe[R]:
        return self._value

    def __iter__(self) -> ta.Iterator[O]:
        return self

    def __next__(self) -> O:
        i = next(self._it)
        try:
            o = self._g.send(i)
        except StopIteration as e:
            self._value = lang.just(e.value)
            raise StopIteration from e
        return o


def genmap(g: ta.Generator[O, I, R], it: ta.Iterable[I]) -> GeneratorMappedIterator[O, I, R]:
    return GeneratorMappedIterator(g, iter(it))


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
    for o in genmap(g, 'abc'):
        print(repr(o))
    print()
