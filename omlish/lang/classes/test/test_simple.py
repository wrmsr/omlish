import pytest

from ..restrict import FinalException
from ..simple import LazySingleton
from ..simple import Marker
from ..simple import Singleton


def test_marker():
    class M(Marker):
        pass

    with pytest.raises(FinalException):
        class N(M):
            pass
    with pytest.raises(TypeError):
        M()

    assert repr(M) == '<M>'

    assert isinstance(M, M)
    assert issubclass(M, M)  # noqa

    class O(Marker):
        pass

    assert isinstance(O, O)
    assert issubclass(O, O)  # noqa

    assert not isinstance(M, O)
    assert not issubclass(M, O)
    assert not isinstance(O, M)
    assert not issubclass(O, M)


def test_singletons():
    for bcls in [Singleton, LazySingleton]:
        foo_init_calls = 0
        foo2_init_calls = 0

        class Foo(bcls):  # type: ignore
            def __init__(self):
                super().__init__()
                nonlocal foo_init_calls
                foo_init_calls += 1

        assert Foo() is Foo()
        assert foo_init_calls == 1

        class Foo2(Foo):
            def __init__(self):
                super().__init__()
                nonlocal foo2_init_calls
                foo2_init_calls += 1

        assert Foo2() is Foo2()
        assert foo2_init_calls == 1
        assert foo_init_calls == 2
