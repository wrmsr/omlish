# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from .config import RemoteConfig
from .spawning import RemoteSpawning


def bind_remote(
        *,
        remote_config: RemoteConfig,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(remote_config),

        inj.bind(remote_config.spawning),

        inj.bind(RemoteSpawning, singleton=True),
    ]

    return inj.as_bindings(*lst)
