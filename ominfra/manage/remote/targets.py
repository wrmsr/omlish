# ruff: noqa: UP006 UP007
import abc
import contextlib
import dataclasses as dc
import typing as ta

from omlish.lite.check import check

from ..commands.base import CommandExecutor
from ..commands.local import LocalCommandExecutor
from ..targets.targets import DirectManageTarget
from ..targets.targets import ManageTarget
from ..targets.connection import ManageTargetConnector
from .connection import PyremoteRemoteExecutionConnector
from .spawning import RemoteSpawning


@dc.dataclass(frozen=True)
class SubprocessManageTargetConnectorImpl(ManageTargetConnector):
    _rec: PyremoteRemoteExecutionConnector

    @contextlib.asynccontextmanager
    async def connect(self, tgt: ManageTarget) -> ta.AsyncGenerator[CommandExecutor, None]:
        rt = RemoteSpawning.Target(
            shell=self.args.shell,
            shell_quote=self.args.shell_quote,
            python=self.args.python,
        )

        ce = await es.enter_async_context(injector[RemoteExecutionConnector].connect(tgt, bs))  # noqa
