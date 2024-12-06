import dataclasses as dc
import typing as ta

from omlish.lite.inject import inj
from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.marshal import ObjMarshalerManager
from omlish.lite.pycharm import pycharm_debug_connect

from ..pyremote import PyremoteBootstrapDriver
from ..pyremote import PyremoteBootstrapOptions
from ..pyremote import pyremote_bootstrap_finalize
from ..pyremote import pyremote_build_bootstrap_cmd
from .commands.base import Command
from .commands.base import CommandExecutor
from .commands.base import build_command_name_map
from .commands.subprocess import SubprocessCommand
from .commands.subprocess import SubprocessCommandExecutor
from .payload import get_payload_src
from .protocol import Channel
from .spawning import PySpawner
from .marshal import install_command_marshaling


##


@dc.dataclass(frozen=True)
class ManageMainConfig:
    pass


def bind_manage_main(
        config: ManageMainConfig,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(config),

    ]

    #

    def build_obj_marshaler_manager(cmds: CommandBindings) -> ObjMarshalerManager:
        msh = ObjMarshalerManager()
        install_command_marshaling(msh, build_command_name_map(cmds))
        return msh

    lst.append(inj.bind(build_obj_marshaler_manager, singleton=True))

    #

    return inj.as_bindings(*lst)
