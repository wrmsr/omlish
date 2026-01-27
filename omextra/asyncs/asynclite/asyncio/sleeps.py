# @omlish-lite
import asyncio
import typing as ta

from ..sleeps import AsyncliteSleeps


##


class AsyncioAsyncliteSleeps(AsyncliteSleeps):
    def sleep(self, delay: float) -> ta.Awaitable[None]:
        return asyncio.sleep(delay)
