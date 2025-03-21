import typing as ta

import anyio

from ... import lang


T = ta.TypeVar('T')


##


class Once:
    def __init__(self) -> None:
        super().__init__()
        self._done = False
        self._lock = anyio.Lock()

    async def do(self, fn: ta.Callable[[], ta.Awaitable[None]]) -> bool:
        if self._done:
            return False
        async with self._lock:
            if self._done:
                return False  # type: ignore
            try:
                await fn()
            finally:
                self._done = True
            return True


##


class Lazy(ta.Generic[T]):
    def __init__(self) -> None:
        super().__init__()
        self._once = Once()
        self._v: lang.Maybe[T] = lang.empty()

    def peek(self) -> lang.Maybe[T]:
        return self._v

    def set(self, v: T) -> None:
        self._v = lang.just(v)

    async def get(self, fn: ta.Callable[[], ta.Awaitable[T]]) -> T:
        async def do():
            self._v = lang.just(await fn())
        await self._once.do(do)
        return self._v.must()


class LazyFn(ta.Generic[T]):
    def __init__(self, fn: ta.Callable[[], ta.Awaitable[T]]) -> None:
        super().__init__()
        self._fn = fn
        self._once = Once()
        self._v: lang.Maybe[T] = lang.empty()

    def peek(self) -> lang.Maybe[T]:
        return self._v

    def set(self, v: T) -> None:
        self._v = lang.just(v)

    async def get(self) -> T:
        async def do():
            self._v = lang.just(await self._fn())
        await self._once.do(do)
        return self._v.must()
