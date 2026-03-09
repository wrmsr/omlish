import asyncio
import threading
import types
import typing as ta

from omlish import check
from omlish.sync.threadrunners import SingleThreadRunner


T = ta.TypeVar('T')


##


class _AwaitInThread:
    def __init__(self, aw: ta.Awaitable[T]) -> None:
        super().__init__()

        self._aw = aw

    def _thread_main(self) -> None:
        pass

    @types.coroutine
    def run(self):
        try:
            a = self._aw.__await__()
            try:
                g = iter(a)
                try:
                    while True:
                        try:
                            f = g.send(None)
                        except StopIteration as ex:
                            return ex.value

                        yield f
                        del f

                finally:
                    if g is not a:
                        g.close()

            finally:
                a.close()  # noqa

        finally:
            self._aw.close()  # noqa


async def await_in_thread(aw: ta.Awaitable[T]) -> T:
    return await _AwaitInThread(aw).run()  # noqa


##


async def oof(s: str) -> str:
    await asyncio.sleep(1)
    return s + '!'


async def _a_main() -> None:
    assert await await_in_thread(oof('hello')) == 'hello!'


if __name__ == '__main__':
    asyncio.run(_a_main())
