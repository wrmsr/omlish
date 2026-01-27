# @omlish-lite
import time

from ..sleeps import AsyncliteSleeps


##


class SyncAsyncliteSleeps(AsyncliteSleeps):
    async def sleep(self, delay: float) -> None:
        time.sleep(delay)  # noqa
