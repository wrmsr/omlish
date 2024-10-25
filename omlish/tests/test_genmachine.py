import typing as ta

import pytest

from .. import check
from ..genmachine import GenMachine


StrGenerator: ta.TypeAlias = ta.Generator[ta.Iterable[str] | None, str, ta.Optional['StrGenerator']]


class FooMachine:
    def __init__(self) -> None:
        super().__init__()
        self._m = GenMachine[str, str](self._state0())

    @property
    def state(self) -> str | None:
        return self._m.state

    def __call__(self, e: str) -> ta.Iterable[str]:
        return self._m(e)

    def _state0(self) -> StrGenerator:
        while True:
            s = yield None
            if s == '?':
                return self._state1()
            if s == '$':
                return None
            yield [s + '!']

    def _state1(self) -> StrGenerator:
        while True:
            s = yield None
            if s == '!':
                return self._state0()
            yield [s + '?']


def test_machine():
    fm = FooMachine()

    assert fm.state == 'FooMachine._state0'
    assert check.single(fm('hi')) == 'hi!'
    assert check.single(fm('bye')) == 'bye!'

    assert check.iterempty(fm('?'))
    assert fm.state == 'FooMachine._state1'
    assert check.single(fm('hi')) == 'hi?'
    assert check.single(fm('bye')) == 'bye?'

    assert check.iterempty(fm('!'))
    assert fm.state == 'FooMachine._state0'
    assert check.single(fm('hi')) == 'hi!'
    assert check.single(fm('bye')) == 'bye!'

    assert check.iterempty(fm('$'))
    assert fm.state is None
    with pytest.raises(GenMachine.ClosedError):  # type: ignore
        next(iter(fm('huh')))


class AbMachine(GenMachine[str, int]):
    def __init__(self) -> None:
        super().__init__(self._a())

    def _a(self):
        while True:
            s = yield None
            if s != 'a':
                raise GenMachine.StateError
            return self._b()

    def _b(self):
        n = 0
        while True:
            try:
                s = yield None
            except GeneratorExit:
                raise GenMachine.StateError from None
            if s == 'a':
                yield (n,)
                return self._a()
            if s != 'b':
                raise GenMachine.StateError
            n += 1


def test_close():
    ios = [
        ('a', []),
        ('b', []),
        ('b', []),
        ('a', [2]),
        ('a', []),
    ]

    m = AbMachine()
    for i, o in ios:
        assert list(m(i)) == o
    with pytest.raises(GenMachine.StateError):
        m.close()

    with pytest.raises(GenMachine.StateError):  # noqa
        with AbMachine() as m:
            for i, o in ios:
                assert list(m(i)) == o
