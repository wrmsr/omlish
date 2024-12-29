# ruff: noqa: UP006 UP007
import contextlib
import os.path
import typing as ta

from omlish.lite.check import check
from omlish.lite.inject import ContextvarInjectorScope
from omlish.lite.inject import Injector
from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from ..commands.injection import bind_command
from .apps import DeployAppManager
from .commands import DeployCommand
from .commands import DeployCommandExecutor
from .conf.inject import bind_deploy_conf
from .config import DeployConfig
from .deploy import DeployDriver
from .deploy import DeployDriverFactory
from .deploy import DeployManager
from .git import DeployGitManager
from .injection import bind_deploy_manager
from .interp import InterpCommand
from .interp import InterpCommandExecutor
from .paths.inject import bind_deploy_paths
from .specs import DeploySpec
from .systemd import DeploySystemdManager
from .tags import DeployTime
from .tmp import DeployHomeAtomics
from .tmp import DeployTmpManager
from .types import DeployHome
from .venvs import DeployVenvManager


##


class DeployInjectorScope(ContextvarInjectorScope):
    pass


def bind_deploy_scope() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind_scope(DeployInjectorScope),
        inj.bind_scope_seed(DeploySpec, DeployInjectorScope),

        inj.bind(DeployDriver, in_=DeployInjectorScope),
    ]

    #

    def provide_deploy_driver_factory(injector: Injector, sc: DeployInjectorScope) -> DeployDriverFactory:
        @contextlib.contextmanager
        def factory(spec: DeploySpec) -> ta.Iterator[DeployDriver]:
            with sc.enter({
                inj.as_key(DeploySpec): spec,
            }):
                yield injector[DeployDriver]
        return DeployDriverFactory(factory)
    lst.append(inj.bind(provide_deploy_driver_factory, singleton=True))

    #

    def provide_deploy_home(deploy: DeploySpec) -> DeployHome:
        hs = check.non_empty_str(deploy.home)
        hs = os.path.expanduser(hs)
        hs = os.path.realpath(hs)
        hs = os.path.abspath(hs)
        return DeployHome(hs)
    lst.append(inj.bind(provide_deploy_home, in_=DeployInjectorScope))

    #

    def provide_deploy_time(deploys: DeployManager) -> DeployTime:
        return deploys.make_deploy_time()
    lst.append(inj.bind(provide_deploy_time, in_=DeployInjectorScope))

    #

    return inj.as_bindings(*lst)


##


def bind_deploy(
        *,
        deploy_config: DeployConfig,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(deploy_config),

        bind_deploy_conf(),

        bind_deploy_paths(),

        bind_deploy_scope(),
    ]

    #

    lst.extend([
        bind_deploy_manager(DeployAppManager),
        bind_deploy_manager(DeployGitManager),
        bind_deploy_manager(DeployManager),
        bind_deploy_manager(DeploySystemdManager),
        bind_deploy_manager(DeployTmpManager),
        bind_deploy_manager(DeployVenvManager),
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
