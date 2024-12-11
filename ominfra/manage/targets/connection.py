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
from ..remote.connection import PyremoteRemoteExecutionConnector
from ..remote.connection import InProcessRemoteExecutionConnector


##


class ManageTargetConnector(abc.ABC):
    @abc.abstractmethod
    def connect(self, tgt: ManageTarget) -> ta.AsyncContextManager[CommandExecutor]:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class LocalManageTargetConnectorImpl(ManageTargetConnector):
    _local_executor: LocalCommandExecutor
    _in_process_connector: InProcessRemoteExecutionConnector
    _pyremote_connector: PyremoteRemoteExecutionConnector

    @contextlib.asynccontextmanager
    async def connect(self, tgt: ManageTarget) -> ta.AsyncGenerator[CommandExecutor, None]:
        lmt = check.isinstance(tgt, LocalManageTarget)

        if lmt.mode == LocalManageTarget.Mode.DIRECT:
            yield self._local_executor

        elif lmt.mode == LocalManageTarget.Mode.SUBPROCESS:
            raise NotImplementedError

        elif lmt.mode == LocalManageTarget.Mode.FAKE_REMOTE:
            with self._in_process_connector.connect() as rce:
                yield rce

        else:
            raise TypeError(lmt.mode)
