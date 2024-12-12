# ruff: noqa: UP006 UP007
import os.path
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from ..commands.inject import bind_command
from .apps import DeployAppManager
from .commands import DeployCommand
from .commands import DeployCommandExecutor
from .config import DeployConfig
from .git import DeployGitManager
from .interp import InterpCommand
from .interp import InterpCommandExecutor
from .types import DeployHome
from .venvs import DeployVenvManager


def bind_deploy(
        *,
        deploy_config: DeployConfig,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(deploy_config),

        inj.bind(DeployAppManager, singleton=True),
        inj.bind(DeployGitManager, singleton=True),
        inj.bind(DeployVenvManager, singleton=True),

        bind_command(DeployCommand, DeployCommandExecutor),
        bind_command(InterpCommand, InterpCommandExecutor),
    ]

    if (dh := deploy_config.deploy_home) is not None:
        dh = os.path.abspath(os.path.expanduser(dh))
        lst.append(inj.bind(dh, key=DeployHome))

    return inj.as_bindings(*lst)
