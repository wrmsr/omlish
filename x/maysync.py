"""
https://github.com/sqlalchemy/sqlalchemy/blob/main/lib/sqlalchemy/util/concurrency.py
"""
import asyncio
import greenlet

from omlish import asyncs


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


async def _a_main():
    print('_a_main')

    print(await a_func(a_callback, 'arg'))
    print(await a_func(s_to_a(callback), 'arg'))

    print(await s_to_a(func)(callback, 'arg'))
    print(await s_to_a(func)(a_to_s(a_callback), 'arg'))


def _main():
    print('_main')

    print(func(callback, 'arg'))
    print(func(a_to_s(a_callback), 'arg'))

    print(a_to_s(a_func)(a_callback, 'arg'))
    print(a_to_s(a_func)(s_to_a(callback), 'arg'))

    #

    asyncio.run(_a_main())


if __name__ == '__main__':
    _main()
