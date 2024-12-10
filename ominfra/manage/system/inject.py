# ruff: noqa: UP006 UP007
import sys
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from .config import SystemConfig
from .types import SystemPlatform


def bind_system(
        *,
        system_config: SystemConfig,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(system_config),
    ]

    platform = system_config.platform or sys.platform
    lst.append(inj.bind(platform, key=SystemPlatform))

    return inj.as_bindings(*lst)
