# @omlish-lite
import abc
import typing as ta

from ...lite.abstract import Abstract


##


class AsyncliteIdentities(Abstract):
    """
    Get the identity of the current task/thread.

    Returns:
     - asyncio: asyncio.Task | None (from asyncio.current_task())
     - sync: threading.Thread (from threading.current_thread())
     - anyio: anyio.TaskInfo (from anyio.get_current_task())
    """

    @abc.abstractmethod
    def current_identity(self) -> ta.Any:
        raise NotImplementedError
