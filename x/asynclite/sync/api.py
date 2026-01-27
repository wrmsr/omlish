# @omlish-lite
from ..api import Asynclite
from .events import SyncAsyncliteEvents
from .locks import SyncAsyncliteLocks
from .sleeps import SyncAsyncliteSleeps


##


class SyncAsynclite(
    SyncAsyncliteEvents,
    SyncAsyncliteLocks,
    SyncAsyncliteSleeps,

    Asynclite,
):
    pass
