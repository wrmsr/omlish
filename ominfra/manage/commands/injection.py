# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from .base import Command
from .base import CommandExecutor
from .base import CommandExecutorRegistration
from .base import CommandRegistration


def bind_command(
        command_cls: ta.Type[Command],
        executor_cls: ta.Optional[ta.Type[CommandExecutor]],
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(CommandRegistration(command_cls), array=True),
    ]

    if executor_cls is not None:
        lst.extend([
            inj.bind(executor_cls, singleton=True),
            inj.bind(CommandExecutorRegistration(command_cls, executor_cls), array=True),
        ])

    return inj.as_bindings(*lst)
