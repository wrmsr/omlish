"""
See:
 - https://github.com/sqlalchemy/sqlalchemy/blob/3ac034057ce621379fb8e0926b851a903d2c7e0b/lib/sqlalchemy/util/concurrency.py
"""  # noqa
import anyio
import pytest

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


async def _test_async_bridge(a_to_s, s_to_a):
    assert (await a_func(a_callback, 'arg')) == 'a_func(arg) -> a_callback(arg)'
    assert (await a_func(s_to_a(callback), 'arg')) == 'a_func(arg) -> callback(arg)'

    assert (await s_to_a(func)(callback, 'arg')) == 'func(arg) -> callback(arg)'
    assert (await s_to_a(func)(a_to_s(a_callback), 'arg')) == 'func(arg) -> a_callback(arg)'


@pytest.mark.asyncio
@pytest.mark.parametrize(('a_to_s', 's_to_a'), [
    (br.a_to_s, br.s_to_a),
    (br.simple_a_to_s, br.simple_s_to_a),
])
async def test_async_bridge_asyncio(a_to_s, s_to_a):
    await _test_async_bridge(a_to_s, s_to_a)


@pytest.mark.trio
@pytest.mark.parametrize(('a_to_s', 's_to_a'), [
    (br.a_to_s, br.s_to_a),
    (br.simple_a_to_s, br.simple_s_to_a),
])
async def test_async_bridge_trio(a_to_s, s_to_a):
    await _test_async_bridge(a_to_s, s_to_a)


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


async def _test_async_bridge2():
    await anyio.sleep(.01)
    assert (await br.s_to_a(func)(br.a_to_s(a_sleep_callback), 'arg')) == 'func(arg) -> a_sleep_callback(arg)'
    assert (await br.s_to_a(func)(sleep_callback, 'arg')) == 'func(arg) -> sleep_callback(arg)'


@pytest.mark.asyncio
async def test_async_bridge2_asyncio():
    await _test_async_bridge2()


@pytest.mark.trio
async def test_async_bridge2_trio():
    await _test_async_bridge2()
