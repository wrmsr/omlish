# @omlish-lite
import asyncio
import typing as ta

from ..identity import AsyncliteIdentity


##


class AsyncioAsyncliteIdentity(AsyncliteIdentity):
    def current_identity(self) -> ta.Any:
        return asyncio.current_task()
