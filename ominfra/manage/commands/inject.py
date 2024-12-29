# ruff: noqa: UP006 UP007
import dataclasses as dc
import functools
import typing as ta

from omlish.lite.inject import Injector
from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from ..config import MainConfig
from ..marshal import ObjMarshalerInstaller
from .base import Command
from .base import CommandExecutor
from .base import CommandExecutorRegistration
from .base import CommandExecutorRegistrations
from .base import CommandNameMap
from .base import CommandRegistration
from .base import CommandRegistrations
from .base import build_command_name_map
from .injection import bind_command
from .local import LocalCommandExecutor
from .marshal import install_command_marshaling
from .ping import PingCommand
from .ping import PingCommandExecutor
from .subprocess import SubprocessCommand
from .subprocess import SubprocessCommandExecutor
from .types import CommandExecutorMap


##


@dc.dataclass(frozen=True)
class _FactoryCommandExecutor(CommandExecutor):
    factory: ta.Callable[[], CommandExecutor]

    def execute(self, i: Command) -> ta.Awaitable[Command.Output]:
        return self.factory().execute(i)


##


def bind_commands(
        *,
        main_config: MainConfig,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
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

    def provide_command_executor_map(
            injector: Injector,
            crs: CommandExecutorRegistrations,
    ) -> CommandExecutorMap:
        dct: ta.Dict[ta.Type[Command], CommandExecutor] = {}

        cr: CommandExecutorRegistration
        for cr in crs:
            if cr.command_cls in dct:
                raise KeyError(cr.command_cls)

            factory = functools.partial(injector.provide, cr.executor_cls)
            if main_config.debug:
                ce = factory()
            else:
                ce = _FactoryCommandExecutor(factory)

            dct[cr.command_cls] = ce

        return CommandExecutorMap(dct)

    lst.extend([
        inj.bind(provide_command_executor_map, singleton=True),

        inj.bind(LocalCommandExecutor, singleton=True, eager=main_config.debug),
    ])

    #

    lst.extend([
        bind_command(PingCommand, PingCommandExecutor),
        bind_command(SubprocessCommand, SubprocessCommandExecutor),
    ])

    #

    return inj.as_bindings(*lst)
