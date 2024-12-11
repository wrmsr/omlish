# ruff: noqa: UP006 UP007
import abc
import contextlib
import dataclasses as dc
import typing as ta

from omlish.lite.check import check

from ..commands.base import CommandExecutor
from ..commands.local import LocalCommandExecutor
from .targets import LocalManageTarget
from .targets import ManageTarget


##


class ManageTargetConnector(abc.ABC):
    @abc.abstractmethod
    def connect(self, tgt: ManageTarget) -> ta.AsyncContextManager[CommandExecutor]:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class LocalManageTargetConnectorImpl(ManageTargetConnector):
    _local_executor: LocalCommandExecutor

    @contextlib.asynccontextmanager
    async def connect(self, tgt: ManageTarget) -> ta.AsyncGenerator[CommandExecutor, None]:
        # DIRECT = enum.auto()
        # SUBPROCESS = enum.auto()
        # FAKE_REMOTE = enum.auto()

        lmt = check.isinstance(tgt, LocalManageTarget)
        yield self._local_executor
