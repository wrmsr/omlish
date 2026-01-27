# @omlish-lite
from ..api import Asynclite
from .events import SyncAsyncliteEvents
from .identity import SyncAsyncliteIdentity
from .locks import SyncAsyncliteLocks
from .queues import SyncAsyncliteQueues
from .semaphores import SyncAsyncliteSemaphores
from .sleeps import SyncAsyncliteSleeps


##


class SyncAsynclite(
    SyncAsyncliteEvents,
    SyncAsyncliteIdentity,
    SyncAsyncliteLocks,
    SyncAsyncliteQueues,
    SyncAsyncliteSemaphores,
    SyncAsyncliteSleeps,

    Asynclite,
):
    pass
