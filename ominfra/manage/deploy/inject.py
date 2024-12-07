# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from ..commands.inject import bind_command
from .command import DeployCommand
from .command import DeployCommandExecutor


def bind_deploy(
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        bind_command(DeployCommand, DeployCommandExecutor),
    ]

    return inj.as_bindings(*lst)
