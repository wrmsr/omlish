# @omlish-lite
import asyncio
import typing as ta

from omlish.lite.abstract import Abstract

from ..base import AsyncliteObject
from ..base import AsyncliteApi


T = ta.TypeVar('T')


##


class AsyncioAsyncliteBase(Abstract):
    @classmethod
    async def _wait_for(cls, aw: ta.Awaitable[T], *, timeout: float | None = None) -> T:
        if timeout is not None:
            try:
                return await asyncio.wait_for(aw, timeout)
            except TimeoutError:
                raise TimeoutError from None  # FIXME: 'our' TimeoutError?

        else:
            return await aw


class AsyncioAsyncliteObject(AsyncliteObject, AsyncioAsyncliteBase, Abstract):
    pass


class AsyncioAsyncliteApi(AsyncliteApi, AsyncioAsyncliteBase, Abstract):
    pass
