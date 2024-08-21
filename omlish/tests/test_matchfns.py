import typing as ta

import pytest

from .. import matchfns as mf


##


def test_matchfns():
    mf0: mf.MatchFn[[int], str] = mf.simple(lambda i: i == 0, lambda _: 'zero!')
    assert mf0(0) == 'zero!'
    with pytest.raises(mf.MatchGuardError):
        mf0(1)

    mf1: mf.MatchFn[[int], str] = mf.simple(lambda i: i == 1, lambda _: 'one!')
    assert mf1(1) == 'one!'
    with pytest.raises(mf.MatchGuardError):
        mf1(0)

    mf0b: mf.MatchFn[[int], str] = mf.simple(lambda i: i == 0, lambda _: 'zero again!')
    assert mf0b(0) == 'zero again!'
    with pytest.raises(mf.MatchGuardError):
        mf0b(1)

    mmf0: mf.MatchFn[[int], str] = mf.multi(mf0, mf1, mf0b)
    assert mmf0(0) == 'zero!'
    assert mmf0(1) == 'one!'
    with pytest.raises(mf.MatchGuardError):
        mmf0(2)

    mmf1: mf.MatchFn[[int], str] = mf.multi(mf0, mf1, mf0b, strict=True)
    with pytest.raises(mf.AmbiguousMatchesError):
        mmf1(0)
    assert mmf1(1) == 'one!'
    with pytest.raises(mf.MatchGuardError):
        mmf1(2)


def test_cached():
    c = 0

    def foo(i: int) -> str:
        nonlocal c
        c += 1
        return str(i)

    mf0: mf.MatchFn[[int], str] = mf.simple(lambda i: 0 <= i < 10, foo)
    assert mf0.guard(0)
    assert not mf0.guard(-1)
    assert not mf0.guard(10)
    assert c == 0
    assert mf0(2) == '2'
    assert c == 1

    mf1 = mf.cached(mf0)
    assert mf1.guard(0)
    assert not mf1.guard(-1)
    assert not mf1.guard(10)
    assert c == 1
    assert mf1(2) == '2'
    assert c == 2
    assert mf1(2) == '2'
    assert c == 2


##


class MatchFnClass(mf.MatchFn[mf.P, mf.T]):
    _cls_match_fn: ta.ClassVar[mf.MultiMatchFn]

    def __init__(self) -> None:
        super().__init__()
        self.__match_fn: mf.MatchFn[mf.P, mf.T] | None = None

    @property
    def _match_fn(self) -> mf.MatchFn[mf.P, mf.T]:
        if (f := self.__match_fn) is None:
            f = self.__match_fn = self._cls_match_fn.__get__(self)
        return f

    def __init_subclass__(cls, strict: bool = False, **kwargs):
        super().__init_subclass__()
        if '_cls_match_fn' in cls.__dict__:
            raise AttributeError('_cls_match_fn')
        d = {}
        for c in cls.__mro__:
            for a, o in c.__dict__.items():
                if isinstance(o, mf.MatchFn) and a not in d:
                    d[a] = o
        cls._cls_match_fn = mf.MultiMatchFn(list(d.values()), strict=strict)

    def guard(self, *args: mf.P.args, **kwargs: mf.P.kwargs) -> bool:
        return self._match_fn.guard(*args, **kwargs)

    def fn(self, *args: mf.P.args, **kwargs: mf.P.kwargs) -> mf.T:
        return self._match_fn.fn(*args, **kwargs)


#


class Foo(MatchFnClass[ta.Any, ta.Any]):
    @mf.simple(lambda self, x: isinstance(x, str))
    def _foo_str(self, s: str) -> str:
        return f'str: {s}'

    @mf.simple(lambda self, x: isinstance(x, int))
    def _foo_int(self, s: int) -> str:
        return f'int: {s}'


def test_class():
    f = Foo()
    assert f('hi') == 'str: hi'
    assert f(0) == 'int: 0'
    with pytest.raises(mf.MatchGuardError):
        assert f(.2)
