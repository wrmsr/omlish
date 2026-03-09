import asyncio
import types
import typing as ta

from omlish.sync.threadrunners import SingleThreadRunner


T = ta.TypeVar('T')


##


@types.coroutine
def _await_in_thread(aw):
    with SingleThreadRunner(name=f'_await_in_thread({aw!r})') as r:
        try:
            a = r.run(lambda: aw.__await__())
            try:
                g = r.run(lambda: iter(a))
                try:
                    while True:
                        try:
                            f = r.run(lambda: g.send(None))
                        except StopIteration as ex:
                            return ex.value

                        yield f
                        del f

                finally:
                    if g is not a:
                        r.run(lambda: g.close())

            finally:
                r.run(lambda: a.close())  # noqa

        finally:
            r.run(lambda: aw.close())  # noqa


async def await_in_thread(aw: ta.Awaitable[T]) -> T:
    return await _await_in_thread(aw)  # noqa


##


async def exclaim(s: str) -> str:
    return s + '!'


async def oof(s: str) -> str:
    # await asyncio.sleep(1)
    return await exclaim(s)


async def _a_main() -> None:
    assert await await_in_thread(oof('hello')) == 'hello!'


if __name__ == '__main__':
    asyncio.run(_a_main())
