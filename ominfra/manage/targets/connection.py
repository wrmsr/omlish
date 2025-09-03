# ruff: noqa: UP006 UP007 UP043 UP045
import abc
import contextlib
import dataclasses as dc
import typing as ta

from omlish.lite.abstract import Abstract
from omlish.lite.check import check

from ..bootstrap import MainBootstrap
from ..commands.base import CommandExecutor
from ..commands.local import LocalCommandExecutor
from ..remote.connection import InProcessRemoteExecutionConnector
from ..remote.connection import PyremoteRemoteExecutionConnector
from ..remote.spawning import RemoteSpawning
from .bestpython import get_best_python_sh
from .targets import DockerManageTarget
from .targets import InProcessManageTarget
from .targets import LocalManageTarget
from .targets import ManageTarget
from .targets import SshManageTarget
from .targets import SubprocessManageTarget


##


class ManageTargetConnector(Abstract):
    @abc.abstractmethod
    def connect(self, tgt: ManageTarget) -> ta.AsyncContextManager[CommandExecutor]:
        raise NotImplementedError

    def _default_python(self, python: ta.Optional[ta.Sequence[str]]) -> ta.Sequence[str]:
        check.not_isinstance(python, str)
        if python is not None:
            return python
        else:
            return ['sh', '-c', get_best_python_sh(), '--']


##


ManageTargetConnectorMap = ta.NewType('ManageTargetConnectorMap', ta.Mapping[ta.Type[ManageTarget], ManageTargetConnector])  # noqa


@dc.dataclass(frozen=True)
class TypeSwitchedManageTargetConnector(ManageTargetConnector):
    connectors: ManageTargetConnectorMap

    def get_connector(self, ty: ta.Type[ManageTarget]) -> ManageTargetConnector:
        for k, v in self.connectors.items():
            if issubclass(ty, k):
                return v
        raise KeyError(ty)

    def connect(self, tgt: ManageTarget) -> ta.AsyncContextManager[CommandExecutor]:
        return self.get_connector(type(tgt)).connect(tgt)


##


@dc.dataclass(frozen=True)
class LocalManageTargetConnector(ManageTargetConnector):
    _local_executor: LocalCommandExecutor
    _in_process_connector: InProcessRemoteExecutionConnector
    _pyremote_connector: PyremoteRemoteExecutionConnector
    _bootstrap: MainBootstrap

    @contextlib.asynccontextmanager
    async def connect(self, tgt: ManageTarget) -> ta.AsyncGenerator[CommandExecutor, None]:
        lmt = check.isinstance(tgt, LocalManageTarget)

        if isinstance(lmt, InProcessManageTarget):
            imt = check.isinstance(lmt, InProcessManageTarget)

            if imt.mode == InProcessManageTarget.Mode.DIRECT:
                yield self._local_executor

            elif imt.mode == InProcessManageTarget.Mode.FAKE_REMOTE:
                async with self._in_process_connector.connect() as rce:
                    yield rce

            else:
                raise TypeError(imt.mode)

        elif isinstance(lmt, SubprocessManageTarget):
            async with self._pyremote_connector.connect(
                    RemoteSpawning.Target(
                        python=self._default_python(lmt.python),
                    ),
                    self._bootstrap,
            ) as rce:
                yield rce

        else:
            raise TypeError(lmt)


##


@dc.dataclass(frozen=True)
class DockerManageTargetConnector(ManageTargetConnector):
    _pyremote_connector: PyremoteRemoteExecutionConnector
    _bootstrap: MainBootstrap

    @contextlib.asynccontextmanager
    async def connect(self, tgt: ManageTarget) -> ta.AsyncGenerator[CommandExecutor, None]:
        dmt = check.isinstance(tgt, DockerManageTarget)

        sh_parts: ta.List[str] = ['docker']
        if dmt.image is not None:
            sh_parts.extend(['run', '-i', dmt.image])
        elif dmt.container_id is not None:
            sh_parts.extend(['exec', '-i', dmt.container_id])
        else:
            raise ValueError(dmt)

        async with self._pyremote_connector.connect(
                RemoteSpawning.Target(
                    shell=' '.join(sh_parts),
                    python=self._default_python(dmt.python),
                ),
                self._bootstrap,
        ) as rce:
            yield rce


##


@dc.dataclass(frozen=True)
class SshManageTargetConnector(ManageTargetConnector):
    _pyremote_connector: PyremoteRemoteExecutionConnector
    _bootstrap: MainBootstrap

    @contextlib.asynccontextmanager
    async def connect(self, tgt: ManageTarget) -> ta.AsyncGenerator[CommandExecutor, None]:
        smt = check.isinstance(tgt, SshManageTarget)

        sh_parts: ta.List[str] = ['ssh']
        if smt.key_file is not None:
            sh_parts.extend(['-i', smt.key_file])
        addr = check.not_none(smt.host)
        if smt.username is not None:
            addr = f'{smt.username}@{addr}'
        sh_parts.append(addr)

        async with self._pyremote_connector.connect(
                RemoteSpawning.Target(
                    shell=' '.join(sh_parts),
                    shell_quote=True,
                    python=self._default_python(smt.python),
                ),
                self._bootstrap,
        ) as rce:
            yield rce
