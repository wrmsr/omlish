import typing as ta

import anyio

from ..identities import AsyncliteIdentities


##


class AnyioAsyncliteIdentities(AsyncliteIdentities):
    def current_identity(self) -> ta.Any:
        return anyio.get_current_task()
