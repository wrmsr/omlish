"""
See:
 - https://github.com/sqlalchemy/sqlalchemy/blob/3ac034057ce621379fb8e0926b851a903d2c7e0b/lib/sqlalchemy/util/concurrency.py
"""  # noqa
import abc
import functools

import anyio
import pytest

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


@pytest.mark.all_async_backends
@pytest.mark.parametrize(('a_to_s', 's_to_a'), [
    (br.a_to_s, br.s_to_a),
    (br.simple_a_to_s, br.simple_s_to_a),
])
async def test_async_bridge(a_to_s, s_to_a):
    assert (await a_func(a_callback, 'arg')) == 'a_func(arg) -> a_callback(arg)'
    assert (await a_func(s_to_a(callback), 'arg')) == 'a_func(arg) -> callback(arg)'

    assert (await s_to_a(func)(callback, 'arg')) == 'func(arg) -> callback(arg)'
    assert (await s_to_a(func)(a_to_s(a_callback), 'arg')) == 'func(arg) -> a_callback(arg)'


@pytest.mark.parametrize(('a_to_s', 's_to_a'), [
    (br.a_to_s, br.s_to_a),
    (br.simple_a_to_s, br.simple_s_to_a),
])
def test_bridge(a_to_s, s_to_a):
    assert func(callback, 'arg') == 'func(arg) -> callback(arg)'
    assert func(a_to_s(a_callback), 'arg') == 'func(arg) -> a_callback(arg)'

    assert a_to_s(a_func)(a_callback, 'arg') == 'a_func(arg) -> a_callback(arg)'
    assert a_to_s(a_func)(s_to_a(callback), 'arg') == 'a_func(arg) -> callback(arg)'


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


@pytest.mark.all_async_backends
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


@pytest.mark.all_async_backends
async def test_async_bridge3():
    n = 4

    fn = a_sleep_callback
    for _ in range(n):
        fn = functools.partial(br.s_to_a(func), br.a_to_s(fn))
        fn = functools.partial(a_func, fn)

    assert (await fn('arg')) == ('a_func(arg) -> func(arg) -> ' * n) + 'a_sleep_callback(arg)'


##


class SLock(abc.ABC):
    @abc.abstractmethod
    def lock(self):
        raise NotImplementedError

    @abc.abstractmethod
    def unlock(self):
        raise NotImplementedError


class ALock(abc.ABC):
    @abc.abstractmethod
    async def lock(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def unlock(self):
        raise NotImplementedError


#


class SLockImpl(SLock):
    def lock(self):
        print(f'{self!r}.lock')

    def unlock(self):
        print(f'{self!r}.unlock')


class ALockImpl(ALock):
    async def lock(self):
        print(f'{self!r}.lock')

    async def unlock(self):
        print(f'{self!r}.unlock')


#


class AtoSLock(SLock):
    def __init__(self, alock: ALock) -> None:
        self.alock = alock

    def lock(self):
        return br.a_to_s(self.alock.lock)()

    def unlock(self):
        return br.a_to_s(self.alock.unlock)()


class StoALock(ALock):
    def __init__(self, slock: SLock) -> None:
        self.slock = slock

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


class ALockThing:
    def __init__(self):
        self.alock = new_a_lock()

    async def run(self):
        await self.alock.lock()
        try:
            print(f'{self!r}.run')
        finally:
            await self.alock.unlock()


def _test_bridge_lock_sync():
    print()
    print('_test_bridge_lock_sync')

    SLockThing().run()

    async def inner():
        await ALockThing().run()

    br.a_to_s(inner)()


async def _test_bridge_lock_async():
    print()
    print('_test_bridge_lock_async')

    await ALockThing().run()

    await br.s_to_a(lambda: SLockThing().run())()


def _test_bridge_lock_sync2():
    print()
    print('_test_bridge_lock_sync2')

    _test_bridge_lock_sync()
    br.a_to_s(_test_bridge_lock_async)()


async def _test_bridge_lock_async2():
    print()
    print('_test_bridge_lock_async2')

    await br.s_to_a(_test_bridge_lock_sync)()
    await _test_bridge_lock_async()


def test_bridge_lock_sync():
    print()
    print('test_bridge_lock_sync')

    _test_bridge_lock_sync2()
    br.a_to_s(_test_bridge_lock_async2)()


@pytest.mark.all_async_backends
async def test_bridge_lock_async():
    print()
    print('test_bridge_lock_async')

    await br.s_to_a(_test_bridge_lock_sync2)()
    await _test_bridge_lock_async2()
