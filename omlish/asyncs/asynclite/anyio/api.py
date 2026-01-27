from ..api import Asynclite
from .events import AnyioAsyncliteEvents
from .identities import AnyioAsyncliteIdentities
from .locks import AnyioAsyncliteLocks
from .queues import AnyioAsyncliteQueues
from .semaphores import AnyioAsyncliteSemaphores
from .sleeps import AnyioAsyncliteSleeps


##


class AnyioAsynclite(
    AnyioAsyncliteEvents,
    AnyioAsyncliteIdentities,
    AnyioAsyncliteLocks,
    AnyioAsyncliteQueues,
    AnyioAsyncliteSemaphores,
    AnyioAsyncliteSleeps,

    Asynclite,
):
    pass
