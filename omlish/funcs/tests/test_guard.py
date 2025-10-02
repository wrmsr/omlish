import typing as ta

from ... import check
from .. import guard as gfs


def test_guard_fns():
    assert gfs.dumb(lambda x: x + 1)(1)() == 2

    def inc_int(x: ta.Any) -> ta.Callable[[], ta.Any] | None:
        if isinstance(x, int):
            return lambda: x + 1
        else:
            return None

    def exclaim_str(s: ta.Any) -> ta.Callable[[], ta.Any] | None:
        if isinstance(s, str):
            return lambda: s + '!'
        else:
            return None

    mgf = gfs.multi(inc_int, exclaim_str)
    assert check.not_none(mgf(1))() == 2
    assert check.not_none(mgf('1'))() == '1!'
    assert mgf(1.0) is None


def test_guard_method():
    class A:
        @gfs.method(strict=True)
        def foo(self, x: ta.Any) -> str:
            raise NotImplementedError

        @foo.register
        def foo_int(self, x: ta.Any) -> ta.Callable[[], str] | None:
            if not isinstance(x, int):
                return None
            return lambda: f'A.foo_int: {x}'

        @foo.register
        def foo_str(self, x: ta.Any) -> ta.Callable[[], str] | None:
            if not isinstance(x, str):
                return None
            return lambda: f'A.foo_str: {x}'

    for _ in range(2):
        a = A()
        assert a.foo(1)() == 'A.foo_int: 1'
        assert a.foo('x')() == 'A.foo_str: x'
        assert a.foo([]) is None

    class B(A):
        @A.foo.register
        def foo_list(self, x: ta.Any) -> ta.Callable[[], str] | None:
            if not isinstance(x, list):
                return None
            return lambda: f'B.foo_list: {x}'

    for _ in range(2):
        b = B()
        assert b.foo(1)() == 'A.foo_int: 1'
        assert b.foo('x')() == 'A.foo_str: x'
        assert b.foo([])() == 'B.foo_list: []'
