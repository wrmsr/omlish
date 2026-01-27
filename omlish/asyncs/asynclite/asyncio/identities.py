# @omlish-lite
import asyncio
import typing as ta

from ..identities import AsyncliteIdentities


##


class AsyncioAsyncliteIdentities(AsyncliteIdentities):
    def current_identity(self) -> ta.Any:
        return asyncio.current_task()
