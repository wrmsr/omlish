# ruff: noqa: UP043
import contextlib
import queue
import typing as ta

import anyio

from ....lite.abstract import Abstract
from ..base import AsyncliteApi
from ..base import AsyncliteObject


##


class AnyioAsyncliteBase(Abstract):
    @classmethod
    @contextlib.contextmanager
    def _translate_exceptions(cls) -> ta.Generator[None, None, None]:
        try:
            yield

        except anyio.WouldBlock as e:
            # anyio raises WouldBlock for both send_nowait and receive_nowait. We need to translate this to queue.Empty
            # or queue.Full depending on context. The caller will need to catch and re-raise the appropriate exception.
            raise queue.Empty from e


class AnyioAsyncliteObject(AsyncliteObject, AnyioAsyncliteBase, Abstract):
    pass


class AnyioAsyncliteApi(AsyncliteApi, AnyioAsyncliteBase, Abstract):
    pass
