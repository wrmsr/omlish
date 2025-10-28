from ..api import Asynclite
from .events import AnyioAsyncliteEvents
from .locks import AnyioAsyncliteLocks
from .queues import AnyioAsyncliteQueues
from .semaphores import AnyioAsyncliteSemaphores


##


class AnyioAsynclite(
    AnyioAsyncliteEvents,
    AnyioAsyncliteLocks,
    AnyioAsyncliteQueues,
    AnyioAsyncliteSemaphores,

    Asynclite,
):
    pass
