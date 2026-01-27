# @omlish-lite
from ...lite.abstract import Abstract
from .events import AsyncliteEvents
from .identities import AsyncliteIdentities
from .locks import AsyncliteLocks
from .queues import AsyncliteQueues
from .semaphores import AsyncliteSemaphores
from .sleeps import AsyncliteSleeps


##


class Asynclite(
    AsyncliteEvents,
    AsyncliteIdentities,
    AsyncliteLocks,
    AsyncliteQueues,
    AsyncliteSemaphores,
    AsyncliteSleeps,

    Abstract,
):
    pass
