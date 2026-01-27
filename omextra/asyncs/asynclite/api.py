# @omlish-lite
from omlish.lite.abstract import Abstract

from .events import AsyncliteEvents
from .locks import AsyncliteLocks
from .queues import AsyncliteQueues
from .semaphores import AsyncliteSemaphores
from .sleeps import AsyncliteSleeps


##


class Asynclite(
    AsyncliteEvents,
    AsyncliteLocks,
    AsyncliteQueues,
    AsyncliteSemaphores,
    AsyncliteSleeps,

    Abstract,
):
    pass
