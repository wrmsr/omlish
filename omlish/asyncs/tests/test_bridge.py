"""
See:
 - https://github.com/sqlalchemy/sqlalchemy/blob/3ac034057ce621379fb8e0926b851a903d2c7e0b/lib/sqlalchemy/util/concurrency.py
"""  # noqa
import abc
import functools
import threading

import anyio
import pytest

from ...testing import pytest as ptu
from .. import anyio as aiu
from .. import bridge as br


##


def callback(arg):
    return f'callback({arg})'


async def a_callback(arg):
    return f'a_callback({arg})'


def func(cb, arg):
    return f'func({arg}) -> {cb(arg)}'


async def a_func(a_cb, arg):
    return f'a_func({arg}) -> {await a_cb(arg)}'


async def _test_trivial_async_bridge(a_to_s, s_to_a):
    assert (await a_func(a_callback, 'arg')) == 'a_func(arg) -> a_callback(arg)'
    assert (await a_func(s_to_a(callback), 'arg')) == 'a_func(arg) -> callback(arg)'

    assert (await s_to_a(func)(callback, 'arg')) == 'func(arg) -> callback(arg)'
    assert (await s_to_a(func)(a_to_s(a_callback), 'arg')) == 'func(arg) -> a_callback(arg)'


def _test_trivial_bridge(a_to_s, s_to_a):
    assert func(callback, 'arg') == 'func(arg) -> callback(arg)'
    assert func(a_to_s(a_callback), 'arg') == 'func(arg) -> a_callback(arg)'

    assert a_to_s(a_func)(a_callback, 'arg') == 'a_func(arg) -> a_callback(arg)'
    assert a_to_s(a_func)(s_to_a(callback), 'arg') == 'a_func(arg) -> callback(arg)'


@pytest.mark.asyncs
async def test_trivial_async_bridge():
    await _test_trivial_async_bridge(br.trivial_a_to_s, br.trivial_s_to_a)


def test_trivial_bridge():
    _test_trivial_bridge(br.trivial_a_to_s, br.trivial_s_to_a)


@ptu.skip.if_cant_import('greenlet')
@pytest.mark.asyncs
async def test_nontrivial_async_bridge():
    await _test_trivial_async_bridge(br.a_to_s, br.s_to_a)


@ptu.skip.if_cant_import('greenlet')
def test_nontrivial_bridge():
    _test_trivial_bridge(br.a_to_s, br.s_to_a)


##


def sleep_callback(arg):
    br.a_to_s(anyio.sleep)(.01)
    return f'sleep_callback({arg})'


async def a_sleep_callback(arg):
    await anyio.sleep(.01)
    return f'a_sleep_callback({arg})'


async def a_sleep_callback2(arg):
    for _ in range(2):
        await anyio.sleep(.01)
    return f'a_sleep_callback2({arg})'


async def a_sleep_callback3(arg):
    await aiu.gather(
        functools.partial(anyio.sleep, .02),
        functools.partial(anyio.sleep, .01),
    )
    return f'a_sleep_callback3({arg})'


async def a_sleep_callback4(arg):
    await aiu.gather(
        functools.partial(anyio.sleep, .02),
        functools.partial(anyio.sleep, .01),
        take_first=True,
    )
    return f'a_sleep_callback4({arg})'


@ptu.skip.if_cant_import('greenlet')
@pytest.mark.asyncs
# @pytest.mark.asyncio
# @pytest.mark.trio
async def test_async_bridge2():
    await anyio.sleep(.01)

    assert (await br.s_to_a(func)(sleep_callback, 'arg')) == 'func(arg) -> sleep_callback(arg)'

    for a_cb in [
        a_sleep_callback,
        a_sleep_callback2,
        a_sleep_callback3,
        a_sleep_callback4,
    ]:
        assert (await br.s_to_a(func)(br.a_to_s(a_cb), 'arg')) == f'func(arg) -> {a_cb.__name__}(arg)'


##


@ptu.skip.if_cant_import('greenlet')
@pytest.mark.asyncs
async def test_async_bridge3():
    n = 4

    fn = a_sleep_callback
    for _ in range(n):
        fn = functools.partial(br.s_to_a(func), br.a_to_s(fn))
        fn = functools.partial(a_func, fn)

    assert (await fn('arg')) == ('a_func(arg) -> func(arg) -> ' * n) + 'a_sleep_callback(arg)'


##


class SLock(abc.ABC):
    lc = 0
    uc = 0

    @abc.abstractmethod
    def lock(self):
        raise NotImplementedError

    @abc.abstractmethod
    def unlock(self):
        raise NotImplementedError


class ALock(abc.ABC):
    lc = 0
    uc = 0

    @abc.abstractmethod
    async def lock(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def unlock(self):
        raise NotImplementedError


#


class SLockImpl(SLock):
    def __init__(self):
        self._lock = threading.RLock()

    def lock(self):
        print(f'{self!r}.lock')
        self._lock.acquire()
        self.lc += 1

    def unlock(self):
        print(f'{self!r}.unlock')
        self._lock.release()
        self.uc += 1


class ALockImpl(ALock):
    def __init__(self):
        self._lock = anyio.Lock()

    async def lock(self):
        print(f'{self!r}.lock')
        await self._lock.acquire()
        self.lc += 1

    async def unlock(self):
        print(f'{self!r}.unlock')
        self._lock.release()
        self.uc += 1


#


class AtoSLock(SLock):
    def __init__(self, alock: ALock) -> None:
        self.alock = alock

    lc = property(lambda self: self.alock.lc)
    uc = property(lambda self: self.alock.uc)

    def lock(self):
        return br.a_to_s(self.alock.lock)()

    def unlock(self):
        return br.a_to_s(self.alock.unlock)()


class StoALock(ALock):
    def __init__(self, slock: SLock) -> None:
        self.slock = slock

    lc = property(lambda self: self.slock.lc)
    uc = property(lambda self: self.slock.uc)

    async def lock(self):
        return await br.s_to_a(self.slock.lock)()

    async def unlock(self):
        return await br.s_to_a(self.slock.unlock)()


#

def new_s_lock() -> SLock:
    if br.is_in_bridge():
        return AtoSLock(ALockImpl())
    else:
        return SLockImpl()


def new_a_lock() -> ALock:
    if br.is_in_bridge():
        return StoALock(SLockImpl())
    else:
        return ALockImpl()


#


class SLockThing:
    def __init__(self):
        self.slock = new_s_lock()

    def run(self):
        self.slock.lock()
        try:
            print(f'{self!r}.run')
        finally:
            self.slock.unlock()
        print()


class ALockThing:
    def __init__(self):
        self.alock = new_a_lock()

    async def run(self):
        await self.alock.lock()
        try:
            print(f'{self!r}.run')
        finally:
            await self.alock.unlock()
        print()


def _assert_s_lock(expects_async):
    sl = SLockThing()
    assert isinstance(sl.slock, AtoSLock) == expects_async
    assert sl.slock.lc == sl.slock.uc == 0
    sl.run()
    assert sl.slock.lc == sl.slock.uc == 1


async def _assert_a_lock(expects_async):
    al = ALockThing()
    assert isinstance(al.alock, StoALock) == (not expects_async)
    assert al.alock.lc == al.alock.uc == 0
    await al.run()
    assert al.alock.lc == al.alock.uc == 1


def _test_bridge_lock_sync(expects_async):
    _assert_s_lock(expects_async)
    br.a_to_s(_assert_a_lock)(expects_async)


async def _test_bridge_lock_async(expects_async):
    await _assert_a_lock(expects_async)
    await br.s_to_a(_assert_s_lock)(expects_async)


def _test_bridge_lock_sync2(expects_async):
    _test_bridge_lock_sync(expects_async)
    br.a_to_s(_test_bridge_lock_async)(expects_async)


async def _test_bridge_lock_async2(expects_async):
    await br.s_to_a(_test_bridge_lock_sync)(expects_async)
    await _test_bridge_lock_async(expects_async)


@ptu.skip.if_cant_import('greenlet')
def test_bridge_lock_sync():
    _test_bridge_lock_sync2(False)
    br.a_to_s(_test_bridge_lock_async2)(False)


@ptu.skip.if_cant_import('greenlet')
@pytest.mark.asyncs
# @pytest.mark.trio
async def test_bridge_lock_async():
    await br.s_to_a(_test_bridge_lock_sync2)(True)
    await _test_bridge_lock_async2(True)
