# @omlish-lite
from ..api import Asynclite
from .events import SyncAsyncliteEvents
from .identities import SyncAsyncliteIdentities
from .locks import SyncAsyncliteLocks
from .queues import SyncAsyncliteQueues
from .semaphores import SyncAsyncliteSemaphores
from .sleeps import SyncAsyncliteSleeps


##


class SyncAsynclite(
    SyncAsyncliteEvents,
    SyncAsyncliteIdentities,
    SyncAsyncliteLocks,
    SyncAsyncliteQueues,
    SyncAsyncliteSemaphores,
    SyncAsyncliteSleeps,

    Asynclite,
):
    pass
