"""
https://github.com/sqlalchemy/sqlalchemy/blob/main/lib/sqlalchemy/util/concurrency.py
"""
import asyncio
import greenlet


def callback():
    return 'callback'


async def a_callback():
    return 'a_callback'


def func(cb):
    return 'func -> ' + cb()


async def a_func(a_cb):
    return 'a_func -> ' + await a_cb()


async def _a_main():
    print(await a_func(a_callback))


def _main():
    print(func(callback))

    asyncio.run(_a_main())


if __name__ == '__main__':
    _main()
