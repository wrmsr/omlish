import contextlib

from ..contextmanagers import ContextManagerLifecycle
from ..contextmanagers import LifecycleContextManager
from ..manager import LifecycleManager


def test_lifecycles():
    @contextlib.contextmanager
    def foo():
        print('foo.enter')
        try:
            yield
        finally:
            print('foo.exit')

    mgr = LifecycleManager()

    f = foo()
    mgr.add(ContextManagerLifecycle(f))

    with LifecycleContextManager(mgr.controller):
        print('inner')
