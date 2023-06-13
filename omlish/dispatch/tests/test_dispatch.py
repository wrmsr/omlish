import abc
import gc

from ..dispatch import Dispatcher


def test_weaks():
    disp: Dispatcher[str] = Dispatcher()

    class A:
        pass

    disp.register('object', [object])
    for _ in range(2):
        assert disp.dispatch(object) == 'object'
        assert disp.dispatch(A) == 'object'

    disp.register('A', [A])
    for _ in range(2):
        assert disp.dispatch(object) == 'object'
        assert disp.dispatch(A) == 'A'

    def inner():
        class B(A):
            pass

        assert len(disp._get_dispatch_cache()) == 2
        for _ in range(2):
            assert disp.dispatch(B) == 'A'
        assert len(disp._get_dispatch_cache()) == 3

    for _ in range(2):
        inner()
        gc.collect()
        assert len(disp._get_dispatch_cache()) == 2


def test_abc():
    disp: Dispatcher[str] = Dispatcher()

    class A(abc.ABC):
        pass

    class B:
        pass

    disp.register('object', [object])
    assert disp.dispatch(A) == 'object'
    assert disp.dispatch(B) == 'object'

    disp.register('A', [A])
    assert disp.dispatch(A) == 'A'
    assert disp.dispatch(B) == 'object'

    A.register(B)  # noqa
    assert disp.dispatch(A) == 'A'
    assert disp.dispatch(B) == 'A'
