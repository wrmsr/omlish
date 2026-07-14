import contextlib

import pytest

from ... import check
from ..base import CallbackAsyncLifecycle
from ..base import CallbackLifecycle
from ..contextmanagers import AsyncContextManagerLifecycle
from ..contextmanagers import AsyncLifecycleContextManager
from ..contextmanagers import ContextManagerLifecycle
from ..contextmanagers import LifecycleContextManager
from ..manager import AsyncLifecycleManager
from ..manager import LifecycleManager
from ..unwrap import unwrap_async_lifecycle
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


@pytest.mark.asyncs('asyncio')
async def test_async_manual_lifecycles():
    mgr = AsyncLifecycleManager()
    await mgr.add(CallbackAsyncLifecycle())


@pytest.mark.asyncs('asyncio')
async def test_async_context_managers():
    @contextlib.asynccontextmanager
    async def foo():
        print('foo.enter')
        try:
            yield
        finally:
            print('foo.exit')

    mgr = AsyncLifecycleManager()

    f = foo()
    await mgr.add(AsyncContextManagerLifecycle(f))

    async with AsyncLifecycleContextManager(check.not_none(unwrap_async_lifecycle(mgr))):
        print('inner')
