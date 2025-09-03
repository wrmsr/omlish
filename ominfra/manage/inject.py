# ruff: noqa: UP006 UP007 UP045
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj
from omlish.lite.marshal import ObjMarshalerManager
from omlish.lite.marshal import new_obj_marshaler_manager

from .bootstrap import MainBootstrap
from .commands.inject import bind_commands
from .config import MainConfig
from .deploy.config import DeployConfig
from .deploy.inject import bind_deploy
from .marshal import ObjMarshalerInstaller
from .marshal import ObjMarshalerInstallers
from .remote.config import RemoteConfig
from .remote.inject import bind_remote
from .system.config import SystemConfig
from .system.inject import bind_system
from .targets.inject import bind_targets


##


def bind_main(
        *,
        main_config: MainConfig = MainConfig(),

        deploy_config: DeployConfig = DeployConfig(),
        remote_config: RemoteConfig = RemoteConfig(),
        system_config: SystemConfig = SystemConfig(),

        main_bootstrap: ta.Optional[MainBootstrap] = None,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(main_config),

        bind_commands(
            main_config=main_config,
        ),

        bind_deploy(
            deploy_config=deploy_config,
        ),

        bind_remote(
            remote_config=remote_config,
        ),

        bind_system(
            system_config=system_config,
        ),

        bind_targets(),
    ]

    #

    if main_bootstrap is not None:
        lst.append(inj.bind(main_bootstrap))

    #

    def build_obj_marshaler_manager(insts: ObjMarshalerInstallers) -> ObjMarshalerManager:
        msh = new_obj_marshaler_manager()
        inst: ObjMarshalerInstaller
        for inst in insts:
            inst.fn(msh)
        return msh

    lst.extend([
        inj.bind(build_obj_marshaler_manager, singleton=True),

        inj.bind_array(ObjMarshalerInstaller),
        inj.bind_array_type(ObjMarshalerInstaller, ObjMarshalerInstallers),
    ])

    #

    return inj.as_bindings(*lst)
