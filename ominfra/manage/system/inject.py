# ruff: noqa: UP006 UP007
import sys
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from ..commands.inject import bind_command
from .commands import CheckSystemPackageCommand
from .commands import CheckSystemPackageCommandExecutor
from .config import SystemConfig
from .packages import AptSystemPackageManager
from .packages import BrewSystemPackageManager
from .packages import SystemPackageManager
from .types import SystemPlatform


def bind_system(
        *,
        system_config: SystemConfig,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(system_config),
    ]

    #

    platform = system_config.platform or sys.platform
    lst.append(inj.bind(platform, key=SystemPlatform))

    #

    if platform == 'linux':
        lst.extend([
            inj.bind(AptSystemPackageManager, singleton=True),
            inj.bind(SystemPackageManager, to_key=AptSystemPackageManager),
        ])

    elif platform == 'darwin':
        lst.extend([
            inj.bind(BrewSystemPackageManager, singleton=True),
            inj.bind(SystemPackageManager, to_key=BrewSystemPackageManager),
        ])

    #

    lst.extend([
        bind_command(CheckSystemPackageCommand, CheckSystemPackageCommandExecutor),
    ])

    #

    return inj.as_bindings(*lst)
