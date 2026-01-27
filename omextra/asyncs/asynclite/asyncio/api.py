# @omlish-lite
from ..api import Asynclite
from .events import AsyncioAsyncliteEvents
from .locks import AsyncioAsyncliteLocks
from .queues import AsyncioAsyncliteQueues
from .semaphores import AsyncioAsyncliteSemaphores
from .sleeps import AsyncioAsyncliteSleeps


##


class AsyncioAsynclite(
    AsyncioAsyncliteEvents,
    AsyncioAsyncliteQueues,
    AsyncioAsyncliteLocks,
    AsyncioAsyncliteSemaphores,
    AsyncioAsyncliteSleeps,

    Asynclite,
):
    pass
