# ruff: noqa: UP006 UP007
import dataclasses as dc
import functools
import typing as ta

from omlish.lite.inject import inj
from omlish.lite.inject import Injector
from omlish.lite.inject import InjectorBindings

from ..marshal import ObjMarshalerInstaller
from .base import Command
from .base import CommandExecutor
from .base import CommandNameMap
from .base import build_command_name_map
from .base import CommandRegistration
from .base import CommandRegistrations
from .base import CommandExecutorRegistration
from .base import CommandExecutorRegistrations
from .execution import CommandExecutionService
from .execution import CommandExecutorMap
from .marshal import install_command_marshaling
from .subprocess import SubprocessCommand
from .subprocess import SubprocessCommandExecutor


##


def bind_command(
        command_cls: ta.Type[Command],
        executor_cls: ta.Optional[ta.Type[CommandExecutor]],
) -> InjectorBindings:
    lst: ta.List[InjectorBindings] = [
        inj.bind(CommandRegistration(command_cls), array=True),
    ]

    if executor_cls is not None:
        lst.extend([
            inj.bind(executor_cls, singleton=True),
            inj.bind(CommandExecutorRegistration(command_cls, executor_cls), array=True),
        ])

    return inj.as_bindings(*lst)


##


@dc.dataclass(frozen=True)
class _FactoryCommandExecutor(CommandExecutor):
    factory: ta.Callable[[], CommandExecutor]

    def execute(self, i: Command) -> Command.Output:
        return self.factory().execute(i)


##


def bind_commands() -> InjectorBindings:
    lst: ta.List[InjectorBindings] = [
        inj.bind_array(CommandRegistration),
        inj.bind_array_type(CommandRegistration, CommandRegistrations),

        inj.bind_array(CommandExecutorRegistration),
        inj.bind_array_type(CommandExecutorRegistration, CommandExecutorRegistrations),

        inj.bind(build_command_name_map, singleton=True),
    ]

    #

    def provide_obj_marshaler_installer(cmds: CommandNameMap) -> ObjMarshalerInstaller:
        return ObjMarshalerInstaller(functools.partial(install_command_marshaling, cmds))

    lst.append(inj.bind(provide_obj_marshaler_installer, array=True))

    #

    def provide_command_executor_map(injector: Injector, crs: CommandExecutorRegistrations) -> CommandExecutorMap:
        dct: ta.Dict[ta.Type[Command], CommandExecutor] = {}
        cr: CommandExecutorRegistration
        for cr in crs:
            if cr.command_cls in dct:
                raise KeyError(cr.command_cls)
            dct[cr.command_cls] = _FactoryCommandExecutor(functools.partial(injector.provide, cr.executor_cls))
        return CommandExecutorMap(dct)

    lst.extend([
        inj.bind(provide_command_executor_map, singleton=True),

        inj.bind(CommandExecutionService, singleton=True),
        inj.bind(CommandExecutor, to_key=CommandExecutionService),
    ])

    #

    for command_cls, executor_cls in [
        (SubprocessCommand, SubprocessCommandExecutor),
    ]:
        lst.append(bind_command(command_cls, executor_cls))

    #

    return inj.as_bindings(*lst)
