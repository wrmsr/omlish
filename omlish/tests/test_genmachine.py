import typing as ta

import pytest

from .. import check
from ..genmachine import GenMachine
from ..genmachine import IllegalStateError


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
    with pytest.raises(IllegalStateError):  # type: ignore
        next(iter(fm('huh')))
