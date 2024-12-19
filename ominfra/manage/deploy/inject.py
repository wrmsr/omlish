# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from ..commands.inject import bind_command
from .apps import DeployAppManager
from .commands import DeployCommand
from .commands import DeployCommandExecutor
from .conf import DeployConfManager
from .config import DeployConfig
from .deploy import DeployManager
from .git import DeployGitManager
from .interp import InterpCommand
from .interp import InterpCommandExecutor
from .paths.inject import bind_deploy_paths
from .paths.owners import DeployPathOwner
from .tmp import DeployHomeAtomics
from .tmp import DeployTmpManager
from .venvs import DeployVenvManager


def bind_deploy(
        *,
        deploy_config: DeployConfig,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(deploy_config),

        bind_deploy_paths(),
    ]

    #

    def bind_manager(cls: type) -> InjectorBindings:
        return inj.as_bindings(
            inj.bind(cls, singleton=True),

            *([inj.bind(DeployPathOwner, to_key=cls, array=True)] if issubclass(cls, DeployPathOwner) else []),
        )

    #

    lst.extend([
        bind_manager(DeployAppManager),

        bind_manager(DeployConfManager),

        bind_manager(DeployGitManager),

        bind_manager(DeployManager),

        bind_manager(DeployTmpManager),

        bind_manager(DeployVenvManager),
    ])

    #

    def provide_deploy_home_atomics(tmp: DeployTmpManager) -> DeployHomeAtomics:
        return DeployHomeAtomics(tmp.get_swapping)
    lst.append(inj.bind(provide_deploy_home_atomics, singleton=True))

    #

    lst.extend([
        bind_command(DeployCommand, DeployCommandExecutor),
        bind_command(InterpCommand, InterpCommandExecutor),
    ])

    #

    return inj.as_bindings(*lst)
