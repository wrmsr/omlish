import pickle
import typing as ta

from ..function import cached_function
from ..property import cached_property


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
            assert c2.d_func() == 0
            assert c2.t_func() == 4
            assert c2.d_prop == 2
            assert c2.t_prop == 5
