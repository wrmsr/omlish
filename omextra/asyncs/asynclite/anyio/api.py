from ..api import Asynclite
from .events import AnyioAsyncliteEvents
from .identity import AnyioAsyncliteIdentity
from .locks import AnyioAsyncliteLocks
from .queues import AnyioAsyncliteQueues
from .semaphores import AnyioAsyncliteSemaphores
from .sleeps import AnyioAsyncliteSleeps


##


class AnyioAsynclite(
    AnyioAsyncliteEvents,
    AnyioAsyncliteIdentity,
    AnyioAsyncliteLocks,
    AnyioAsyncliteQueues,
    AnyioAsyncliteSemaphores,
    AnyioAsyncliteSleeps,

    Asynclite,
):
    pass
