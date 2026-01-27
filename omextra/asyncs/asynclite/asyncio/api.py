# @omlish-lite
from ..api import Asynclite
from .events import AsyncioAsyncliteEvents
from .identity import AsyncioAsyncliteIdentity
from .locks import AsyncioAsyncliteLocks
from .queues import AsyncioAsyncliteQueues
from .semaphores import AsyncioAsyncliteSemaphores
from .sleeps import AsyncioAsyncliteSleeps


##


class AsyncioAsynclite(
    AsyncioAsyncliteEvents,
    AsyncioAsyncliteIdentity,
    AsyncioAsyncliteLocks,
    AsyncioAsyncliteQueues,
    AsyncioAsyncliteSemaphores,
    AsyncioAsyncliteSleeps,

    Asynclite,
):
    pass
