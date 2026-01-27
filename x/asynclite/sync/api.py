# @omlish-lite
from ..api import Asynclite
from .events import SyncAsyncliteEvents
from .locks import SyncAsyncliteLocks
from .queues import SyncAsyncliteQueues
from .semaphores import SyncAsyncliteSemaphores
from .sleeps import SyncAsyncliteSleeps


##


class SyncAsynclite(
    SyncAsyncliteEvents,
    SyncAsyncliteLocks,
    SyncAsyncliteQueues,
    SyncAsyncliteSemaphores,
    SyncAsyncliteSleeps,

    Asynclite,
):
    pass
