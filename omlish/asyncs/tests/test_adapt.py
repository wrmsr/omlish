"""
See:
 - https://github.com/sqlalchemy/sqlalchemy/blob/3ac034057ce621379fb8e0926b851a903d2c7e0b/lib/sqlalchemy/util/concurrency.py
"""  # noqa
import pytest

from .. import asyncs


##


def s_to_a(fn):
    async def inner(*args, **kwargs):
        return fn(*args, **kwargs)
    return inner


def a_to_s(fn):
    def inner(*args, **kwargs):
        return asyncs.sync_await(fn, *args, **kwargs)
    return inner


##


def callback(arg):
    return f'callback({arg})'


async def a_callback(arg):
    return f'a_callback({arg})'


def func(cb, arg):
    return f'func({arg}) -> {cb(arg)}'


async def a_func(a_cb, arg):
    return f'a_func({arg}) -> {await a_cb(arg)}'


@pytest.mark.asyncio
async def test_async_adapt():
    assert (await a_func(a_callback, 'arg')) == 'a_func(arg) -> a_callback(arg)'
    assert (await a_func(s_to_a(callback), 'arg')) == 'a_func(arg) -> callback(arg)'

    assert (await s_to_a(func)(callback, 'arg')) == 'func(arg) -> callback(arg)'
    assert (await s_to_a(func)(a_to_s(a_callback), 'arg')) == 'func(arg) -> a_callback(arg)'


def test_adapt():
    assert func(callback, 'arg') == 'func(arg) -> callback(arg)'
    assert func(a_to_s(a_callback), 'arg') == 'func(arg) -> a_callback(arg)'

    assert a_to_s(a_func)(a_callback, 'arg') == 'a_func(arg) -> a_callback(arg)'
    assert a_to_s(a_func)(s_to_a(callback), 'arg') == 'a_func(arg) -> callback(arg)'
