# ruff: noqa: UP041 UP043 UP045
# @omlish-lite
import asyncio
import contextlib
import queue
import typing as ta

from ....lite.abstract import Abstract
from ..base import AsyncliteApi
from ..base import AsyncliteObject


T = ta.TypeVar('T')


##


class AsyncioAsyncliteBase(Abstract):
    @classmethod
    @contextlib.contextmanager
    def _translate_exceptions(cls) -> ta.Generator[None, None, None]:
        try:
            yield

        except asyncio.TimeoutError as e:
            raise TimeoutError from e

        except asyncio.QueueEmpty as e:
            raise queue.Empty from e

        except asyncio.QueueFull as e:
            raise queue.Full from e

    @classmethod
    async def _wait_for(cls, aw: ta.Awaitable[T], *, timeout: ta.Optional[float] = None) -> T:
        if timeout is not None:
            with cls._translate_exceptions():
                return await asyncio.wait_for(aw, timeout)

        else:
            return await aw


class AsyncioAsyncliteObject(AsyncliteObject, AsyncioAsyncliteBase, Abstract):
    pass


class AsyncioAsyncliteApi(AsyncliteApi, AsyncioAsyncliteBase, Abstract):
    pass
