# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj
from omlish.lite.marshal import ObjMarshalerManager

from .commands.inject import bind_commands
from .config import MainConfig
from .deploy.inject import bind_deploy
from .marshal import ObjMarshalerInstaller
from .marshal import ObjMarshalerInstallers
from .remote.config import RemoteConfig
from .remote.inject import bind_remote


##


def bind_main(
        *,
        main_config: MainConfig,
        remote_config: RemoteConfig,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(main_config),

        bind_commands(
            main_config=main_config,
        ),

        bind_remote(
            remote_config=remote_config,
        ),

        bind_deploy(),
    ]

    #

    def build_obj_marshaler_manager(insts: ObjMarshalerInstallers) -> ObjMarshalerManager:
        msh = ObjMarshalerManager()
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
