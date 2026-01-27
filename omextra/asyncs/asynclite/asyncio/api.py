# @omlish-lite
from ..api import Asynclite
from .events import AsyncioAsyncliteEvents
from .identities import AsyncioAsyncliteIdentities
from .locks import AsyncioAsyncliteLocks
from .queues import AsyncioAsyncliteQueues
from .semaphores import AsyncioAsyncliteSemaphores
from .sleeps import AsyncioAsyncliteSleeps


##


class AsyncioAsynclite(
    AsyncioAsyncliteEvents,
    AsyncioAsyncliteIdentities,
    AsyncioAsyncliteLocks,
    AsyncioAsyncliteQueues,
    AsyncioAsyncliteSemaphores,
    AsyncioAsyncliteSleeps,

    Asynclite,
):
    pass
