# @omlish-lite
import threading
import typing as ta

from ..identity import AsyncliteIdentity


##


class SyncAsyncliteIdentity(AsyncliteIdentity):
    def current_identity(self) -> ta.Any:
        return threading.current_thread()
