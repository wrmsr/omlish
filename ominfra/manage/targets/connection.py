# ruff: noqa: UP006 UP007
import abc
import contextlib
import dataclasses as dc
import typing as ta

from omlish.lite.check import check

from ..bootstrap import MainBootstrap
from ..commands.base import CommandExecutor
from ..commands.local import LocalCommandExecutor
from ..remote.connection import InProcessRemoteExecutionConnector
from ..remote.connection import PyremoteRemoteExecutionConnector
from ..remote.spawning import RemoteSpawning
from .targets import DockerManageTarget
from .targets import InProcessConnectorTarget
from .targets import LocalManageTarget
from .targets import ManageTarget
from .targets import SshManageTarget
from .targets import SubprocessManageTarget


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
    _bootstrap: MainBootstrap

    @contextlib.asynccontextmanager
    async def connect(self, tgt: ManageTarget) -> ta.AsyncGenerator[CommandExecutor, None]:
        lmt = check.isinstance(tgt, LocalManageTarget)

        if isinstance(lmt, InProcessConnectorTarget):
            imt = check.isinstance(lmt, InProcessConnectorTarget)

            if imt.mode == InProcessConnectorTarget.Mode.DIRECT:
                yield self._local_executor

            elif imt.mode == InProcessConnectorTarget.Mode.FAKE_REMOTE:
                async with self._in_process_connector.connect() as rce:
                    yield rce

            else:
                raise TypeError(imt.modd)

        elif isinstance(lmt, SubprocessManageTarget):
            async with self._pyremote_connector.connect(
                    RemoteSpawning.Target(
                        python=lmt.python,
                    ),
                    self._bootstrap,
            ) as rce:
                yield rce

        else:
            raise TypeError(lmt.mode)


##


@dc.dataclass(frozen=True)
class DockerManageTargetConnectorImpl(ManageTargetConnector):
    @contextlib.asynccontextmanager
    async def connect(self, tgt: ManageTarget) -> ta.AsyncGenerator[CommandExecutor, None]:
        dmt = check.isinstance(tgt, DockerManageTarget)

        raise NotImplementedError
        yield None  # noqa


##


@dc.dataclass(frozen=True)
class SshManageTargetConnectorImpl(ManageTargetConnector):
    @contextlib.asynccontextmanager
    async def connect(self, tgt: ManageTarget) -> ta.AsyncGenerator[CommandExecutor, None]:
        smt = check.isinstance(tgt, SshManageTarget)

        raise NotImplementedError
        yield None  # noqa
