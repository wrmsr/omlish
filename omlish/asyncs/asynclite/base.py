# @omlish-lite
import abc
import typing as ta

from ...lite.abstract import Abstract


AsyncliteCloseableT = ta.TypeVar('AsyncliteCloseableT', bound='AsyncliteCloseable')


##


class AsyncliteObject(Abstract):
    pass


class AsyncliteApi(Abstract):
    pass


##


class AsyncliteCloseable(Abstract):
    async def __aenter__(self: AsyncliteCloseableT) -> AsyncliteCloseableT:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()

    @abc.abstractmethod
    def aclose(self) -> ta.Awaitable[None]:
        raise NotImplementedError
