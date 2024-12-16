# ruff: noqa: UP006 UP007
import os.path
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj
from omlish.os.atomics import AtomicPathSwapping

from ..commands.inject import bind_command
from .apps import DeployAppManager
from .commands import DeployCommand
from .commands import DeployCommandExecutor
from .conf import DeployConfManager
from .config import DeployConfig
from .git import DeployGitManager
from .interp import InterpCommand
from .interp import InterpCommandExecutor
from .paths import DeployPathOwner
from .paths import DeployPathOwners
from .tmp import DeployTmpManager
from .types import DeployHome
from .venvs import DeployVenvManager


def bind_deploy(
        *,
        deploy_config: DeployConfig,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(deploy_config),
    ]

    #

    def bind_manager(cls: type) -> InjectorBindings:
        return inj.as_bindings(
            inj.bind(cls, singleton=True),

            *([inj.bind(DeployPathOwner, to_key=cls, array=True)] if issubclass(cls, DeployPathOwner) else []),
        )

    lst.extend([
        inj.bind_array(DeployPathOwner),
        inj.bind_array_type(DeployPathOwner, DeployPathOwners),
    ])

    #

    lst.extend([
        bind_manager(DeployAppManager),

        bind_manager(DeployConfManager),

        bind_manager(DeployGitManager),

        bind_manager(DeployTmpManager),
        inj.bind(AtomicPathSwapping, to_key=DeployTmpManager),

        bind_manager(DeployVenvManager),
    ])

    #

    lst.extend([
        bind_command(DeployCommand, DeployCommandExecutor),
        bind_command(InterpCommand, InterpCommandExecutor),
    ])

    #

    if (dh := deploy_config.deploy_home) is not None:
        dh = os.path.abspath(os.path.expanduser(dh))
        lst.append(inj.bind(dh, key=DeployHome))

    return inj.as_bindings(*lst)
