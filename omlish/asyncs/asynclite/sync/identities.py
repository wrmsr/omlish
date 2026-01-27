# @omlish-lite
import threading
import typing as ta

from ..identities import AsyncliteIdentities


##


class SyncAsyncliteIdentities(AsyncliteIdentities):
    def current_identity(self) -> ta.Any:
        return threading.current_thread()
