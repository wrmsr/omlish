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

        assert len(disp._dispatch_cache) == 2
        for _ in range(2):
            assert disp.dispatch(B) == 'A'
        assert len(disp._dispatch_cache) == 3

    for _ in range(2):
        inner()
        gc.collect()
        assert len(disp._dispatch_cache) == 2
