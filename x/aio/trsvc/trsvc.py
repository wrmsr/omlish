"""
https://trio.readthedocs.io/en/latest/reference-core.html#custom-supervisors
"""
import functools  # noqa
import typing as ta

from omlish import lang  # noqa
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


class AwaitableEvent(ta.Protocol):
    def is_set(self) -> bool: ...
    def set(self) -> None: ...
    async def wait(self) -> None: ...


async def await_any_idx(*fns: ta.Callable[..., ta.Awaitable]) -> tuple[int, ta.Any]:
    ret: list[tuple[int, ta.Any]] = []

    async def await_to(i, fn, *args, **kwargs):
        v = await fn(*args, **kwargs)
        ret.append((i, v))

    await tu.wait_any(*[
        functools.partial(await_to, i, fn)
        for i, fn in enumerate(fns)
    ])

    return ret[0]


async def printer(stop: AwaitableEvent, name: str, delay_s: float):
    i = 0
    while not stop.is_set():
        # idx, _ = await await_any_idx(
        #     functools.partial(trio.sleep, delay_s),
        #     functools.partial(stop.wait),
        # )
        # if idx == 1:
        #     print(f'{name} stopped')
        #     break

        with trio.move_on_after(delay_s):
            await stop.wait()
            print(f'{name} stopped')
            break

        print(f'{name} {i}')  # noqa
        i += 1


async def stopper(stop: AwaitableEvent, delay_s: float):
    await trio.sleep(delay_s)
    stop.set()


async def _a_main():
    stop = trio.Event()
    async with trio.open_nursery() as nursery:
        nursery.start_soon(printer, stop, 'printer0', 10.)
        nursery.start_soon(printer, stop, 'printer1', 1.3)
        nursery.start_soon(stopper, stop, 5.)


if __name__ == '__main__':
    trio.run(_a_main)
