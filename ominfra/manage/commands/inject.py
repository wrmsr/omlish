import dataclasses as dc
import typing as ta

from omlish.lite.inject import inj
from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.marshal import ObjMarshalerManager
from omlish.lite.pycharm import pycharm_debug_connect

from .base import Command
from .base import CommandExecutor
from .base import CommandNameMap
from .base import build_command_name_map
from .subprocess import SubprocessCommand
from .subprocess import SubprocessCommandExecutor


##


@dc.dataclass(frozen=True)
class CommandBinding:
    command_cls: ta.Type[Command]


CommandBindings = ta.NewType('CommandBindings', ta.Sequence[CommandBinding])


##


@dc.dataclass(frozen=True)
class CommandExecutorBinding:
    command_cls: ta.Type[Command]
    executor_cls: ta.Type[CommandExecutor]


CommandExecutorBindings = ta.NewType('CommandExecutorBindings', ta.Sequence[CommandExecutorBinding])


##


def bind_command(
        command_cls: ta.Type[Command],
        executor_cls: ta.Optional[ta.Type[CommandExecutor]],
) -> InjectorBindings:
    lst: ta.List[InjectorBindings] = [
        inj.bind(CommandBinding(command_cls), array=True),
    ]

    if executor_cls is not None:
        lst.append(inj.bind(CommandExecutorBinding(executor_cls), array=True))

    return inj.bind(*lst)


##


def bind_commands() -> InjectorBindings:
    lst: ta.List[InjectorBindings] = [
        inj.bind_array(CommandBinding),
        inj.bind_array_type(CommandBinding, CommandBindings),

        inj.bind_array(CommandExecutorBinding),
        inj.bind_array_type(CommandExecutorBinding, CommandExecutorBindings),
    ]

    #

    def provide_command_name_map(cbs: CommandBindings) -> CommandNameMap:
        return build_command_name_map([b.command_cls for b in cbs])
    lst.append(inj.bind(provide_command_name_map, singleton=True))

    #

    for command_cls, executor_cls in [
        (SubprocessCommand, SubprocessCommandExecutor),
    ]:
        lst.append(bind_command(command_cls, executor_cls))

    #

    return inj.as_bindings(*lst)
