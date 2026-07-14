import typing as ta

import anyio

from ..sleeps import AsyncliteSleeps


##


class AnyioAsyncliteSleeps(AsyncliteSleeps):
    def sleep(self, delay: float) -> ta.Awaitable[None]:
        return anyio.sleep(delay)
