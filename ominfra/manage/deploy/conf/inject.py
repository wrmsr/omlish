# ruff: noqa: UP006 UP007 UP045
import typing as ta

from omcore.lite.inject import InjectorBindingOrBindings
from omcore.lite.inject import InjectorBindings
from omcore.lite.inject import inj

from ..injection import bind_deploy_manager
from .manager import DeployConfManager


##


def bind_deploy_conf() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        bind_deploy_manager(DeployConfManager),
    ]

    return inj.as_bindings(*lst)
