# ruff: noqa: UP006 UP007
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
from .platforms import Platform
from .platforms import LinuxPlatform
from .platforms import DarwinPlatform
from .platforms import get_system_platform


def bind_system(
        *,
        system_config: SystemConfig,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(system_config),
    ]

    #

    platform = system_config.platform or get_system_platform()
    lst.append(inj.bind(platform, key=Platform))

    #

    if isinstance(platform, LinuxPlatform):
        lst.extend([
            inj.bind(AptSystemPackageManager, singleton=True),
            inj.bind(SystemPackageManager, to_key=AptSystemPackageManager),
        ])

    elif isinstance(platform ,DarwinPlatform):
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
