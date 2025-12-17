import contextlib

from ... import check
from ..base import CallbackLifecycle
from ..contextmanagers import ContextManagerLifecycle
from ..contextmanagers import LifecycleContextManager
from ..manager import LifecycleManager
from ..unwrap import unwrap_lifecycle


def test_manual_lifecycles():
    mgr = LifecycleManager()
    mgr.add(CallbackLifecycle())


def test_context_managers():
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

    with LifecycleContextManager(check.not_none(unwrap_lifecycle(mgr))):
        print('inner')
