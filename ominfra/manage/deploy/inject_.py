# ruff: noqa: UP006 UP007
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from .paths.owners import DeployPathOwner


def bind_deploy_manager(cls: type) -> InjectorBindings:
    return inj.as_bindings(
        inj.bind(cls, singleton=True),

        *([inj.bind(DeployPathOwner, to_key=cls, array=True)] if issubclass(cls, DeployPathOwner) else []),
    )
