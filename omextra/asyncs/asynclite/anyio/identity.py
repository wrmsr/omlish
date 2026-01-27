# @omlish-lite
import typing as ta

import anyio

from ..identity import AsyncliteIdentity


##


class AnyioAsyncliteIdentity(AsyncliteIdentity):
    def current_identity(self) -> ta.Any:
        return anyio.get_current_task()
