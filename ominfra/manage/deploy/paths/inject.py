# ruff: noqa: UP006 UP007 UP045
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from .manager import DeployPathsManager
from .owners import DeployPathOwner
from .owners import DeployPathOwners


##


def bind_deploy_paths() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind_array(DeployPathOwner),
        inj.bind_array_type(DeployPathOwner, DeployPathOwners),

        inj.bind(DeployPathsManager, singleton=True),
    ]

    return inj.as_bindings(*lst)
