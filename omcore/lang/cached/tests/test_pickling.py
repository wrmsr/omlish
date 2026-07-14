import pickle
import typing as ta

from ..function import cached_function
from ..property import cached_property


##


class _PickleTestClass:
    _c = 0

    @classmethod
    def c(cls) -> int:
        c = cls._c
        cls._c += 1
        return c

    @cached_function()
    def d_func(self) -> int:
        return self.c()

    @cached_function(transient=True)
    def t_func(self) -> int:
        return self.c()

    @cached_property()
    def d_prop(self) -> int:
        return self.c()

    @cached_property(transient=True)
    def t_prop(self) -> int:
        return self.c()


class _PickleTestClass2(_PickleTestClass):
    _c = 0


def test_pickling():
    c: ta.Any
    for c in [
        _PickleTestClass(),
        _PickleTestClass2(),
    ]:
        for _ in range(2):
            assert c.d_func() == 0
            assert c.t_func() == 1
            assert c.d_prop == 2
            assert c.t_prop == 3

        c2 = pickle.loads(pickle.dumps(c))  # noqa
        assert type(c2) is type(c)

        for _ in range(2):
            assert c2.d_func() == 0  # non-transient func cache survived
            assert c2.t_func() == 4  # transient func cache reset -> recomputed
            assert c2.d_prop == 2  # non-transient prop cache survived
            assert c2.t_prop == 5  # transient prop cache reset -> recomputed


##


class _NoAccessPickleClass:
    @cached_function()
    def f(self) -> int:
        return 42


def test_pickling_without_prior_access():
    # An instance whose cached method was never accessed has no bound wrapper in its __dict__; it should pickle cleanly
    # and rebind fresh on the other side.
    c = _NoAccessPickleClass()
    c2 = pickle.loads(pickle.dumps(c))  # noqa
    assert c2.f() == 42
    assert c2.f() == 42


##


_FREE_HOLDER_CALLS: dict[_FreeHolder, int] = {}


class _FreeHolder:
    def __init__(self, name: str) -> None:
        self.name = name

    def m(self, x):
        _FREE_HOLDER_CALLS[self] = _FREE_HOLDER_CALLS.get(self, 0) + 1
        return x + 1


def test_free_bound_method_pickling():
    h = _FreeHolder('test_free_bound_method_pickling')
    cf = cached_function(h.m)
    assert h not in _FREE_HOLDER_CALLS
    assert cf(5) == 6
    assert _FREE_HOLDER_CALLS[h] == 1
    assert cf(5) == 6
    assert _FREE_HOLDER_CALLS[h] == 1

    initial_free_holders = set(_FREE_HOLDER_CALLS)
    cf2 = pickle.loads(pickle.dumps(cf))  # noqa
    assert dict(cf2._values) == {5: 6}  # noqa  # non-transient cache survived the round trip
    assert set(_FREE_HOLDER_CALLS) == initial_free_holders

    assert cf2(5) == 6
    assert set(_FREE_HOLDER_CALLS) == initial_free_holders

    assert cf2(6) == 7
    [h2] = set(_FREE_HOLDER_CALLS) - initial_free_holders
    assert _FREE_HOLDER_CALLS[h2] == 1
    assert h2.name == h.name


def test_free_bound_method_transient_pickling():
    h = _FreeHolder('test_free_bound_method_transient_pickling')
    cf = cached_function(h.m, transient=True)
    assert h not in _FREE_HOLDER_CALLS
    assert cf(5) == 6
    assert _FREE_HOLDER_CALLS[h] == 1
    # assert dict(cf._values) == {(5,): 6}  # type: ignore  # noqa

    initial_free_holders = set(_FREE_HOLDER_CALLS)
    cf2 = pickle.loads(pickle.dumps(cf))  # noqa
    assert dict(cf2._values) == {}  # noqa  # transient cache dropped on pickle
    assert set(_FREE_HOLDER_CALLS) == initial_free_holders

    assert cf2(5) == 6  # recomputed fresh
    [h2] = set(_FREE_HOLDER_CALLS) - initial_free_holders
    assert _FREE_HOLDER_CALLS[h2] == 1
    assert h2.name == h.name
