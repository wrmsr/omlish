import pickle

import pytest

from ..restrict import FinalTypeError
from ..restrict import NotPicklable
from ..simple import LazySingleton
from ..simple import Marker
from ..simple import Singleton


def test_marker():
    class M(Marker):
        pass

    with pytest.raises(FinalTypeError):
        class N(M):
            pass
    with pytest.raises(TypeError):
        M()

    assert repr(M) == '<M>'

    assert isinstance(M, M)
    assert issubclass(M, M)  # type: ignore

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
            def __init__(self) -> None:
                super().__init__()
                nonlocal foo_init_calls
                foo_init_calls += 1

        assert Foo() is Foo()
        assert foo_init_calls == 1

        class Foo2(Foo):
            def __init__(self) -> None:
                super().__init__()
                nonlocal foo2_init_calls
                foo2_init_calls += 1

        assert Foo2() is Foo2()
        assert foo2_init_calls == 1
        assert foo_init_calls == 2


class UnpicklableSentinel(NotPicklable):
    pass


PICKLED_SENTINEL = UnpicklableSentinel()


_NUM_PICKLED_SINGLETON_INSTANTIATIONS = 0


class PickledSingleton(Singleton):
    def __init__(self) -> None:
        super().__init__()
        self.barf = PICKLED_SENTINEL
        global _NUM_PICKLED_SINGLETON_INSTANTIATIONS
        _NUM_PICKLED_SINGLETON_INSTANTIATIONS += 1


def test_singleton_pickling():
    assert _NUM_PICKLED_SINGLETON_INSTANTIATIONS == 1
    obj = PickledSingleton()
    assert _NUM_PICKLED_SINGLETON_INSTANTIATIONS == 1
    assert obj is PickledSingleton()
    pkl = pickle.dumps(obj)
    obj2 = pickle.loads(pkl)  # noqa
    assert obj2 is PickledSingleton()
    assert _NUM_PICKLED_SINGLETON_INSTANTIATIONS == 1


_NUM_PICKLED_LAZY_SINGLETON_INSTANTIATIONS = 0


class PickledLazySingleton(LazySingleton):
    def __init__(self) -> None:
        super().__init__()
        self.barf = PICKLED_SENTINEL
        global _NUM_PICKLED_LAZY_SINGLETON_INSTANTIATIONS
        _NUM_PICKLED_LAZY_SINGLETON_INSTANTIATIONS += 1


def test_lazy_singleton_pickling():
    assert _NUM_PICKLED_LAZY_SINGLETON_INSTANTIATIONS == 0
    obj = PickledLazySingleton()
    assert _NUM_PICKLED_LAZY_SINGLETON_INSTANTIATIONS == 1
    assert obj is PickledLazySingleton()
    pkl = pickle.dumps(obj)
    obj2 = pickle.loads(pkl)  # noqa
    assert obj2 is PickledLazySingleton()
    assert _NUM_PICKLED_LAZY_SINGLETON_INSTANTIATIONS == 1
