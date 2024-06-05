"""
https://trio.readthedocs.io/en/latest/reference-core.html#custom-supervisors
"""
import functools  # noqa
import typing as ta

import trio
from .. import trio_util as tu  # noqa


# async def race(*async_fns):
#     if not async_fns:
#         raise ValueError("must pass at least one argument")
#
#     winner = None
#
#     async def jockey(async_fn, cancel_scope):
#         nonlocal winner
#         winner = await async_fn()
#         cancel_scope.cancel()
#
#     async with trio.open_nursery() as nursery:
#         for async_fn in async_fns:
#             nursery.start_soon(jockey, async_fn, nursery.cancel_scope)
#
#     return winner


async def await_as(rv, fn, *args, **kwargs):
    await fn(*args, **kwargs)
    return rv


class AwaitableEvent(ta.Protocol):
    def is_set(self) -> bool: ...
    def set(self) -> None: ...
    async def wait(self) -> None: ...


async def printer0(stop: AwaitableEvent):
    while not stop.is_set():
        idx = await tu.wait_any(
            functools.partial(await_as, 0, trio.sleep, .3),
            functools.partial(await_as, 1, stop.wait),
        )
        if idx == 1:
            print('printer0 stopped')
            break
        print('printer0')


async def printer1(stop: AwaitableEvent):
    while not stop.is_set():
        idx = await tu.wait_any(
            functools.partial(await_as, 0, trio.sleep, .5),
            functools.partial(await_as, 1, stop.wait),
        )
        if idx == 1:
            print('printer1 stopped')
            break
        print('printer1')


async def stopper(stop: AwaitableEvent):
    await trio.sleep(5)
    stop.set()


async def _a_main():
    stop = trio.Event()
    async with trio.open_nursery() as nursery:
        nursery.start_soon(printer0, stop)
        nursery.start_soon(printer1, stop)
        nursery.start_soon(stopper, stop)


if __name__ == '__main__':
    trio.run(_a_main)
