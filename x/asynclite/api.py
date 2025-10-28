# @omlish-lite
from omlish.lite.abstract import Abstract

from .events import AsyncliteEvents
from .locks import AsyncliteLocks
from .queues import AsyncliteQueues
from .semaphores import AsyncliteSemaphores


##


class Asynclite(
    AsyncliteEvents,
    AsyncliteLocks,
    AsyncliteQueues,
    AsyncliteSemaphores,

    Abstract,
):
    pass
