# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from .config import RemoteConfig
from .execution import RemoteExecution
from .payload import RemoteExecutionPayloadFile
from .spawning import PyremoteRemoteSpawning
from .spawning import RemoteSpawning


def bind_remote(
        *,
        remote_config: RemoteConfig,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(remote_config),

        inj.bind(PyremoteRemoteSpawning, singleton=True),
        inj.bind(RemoteSpawning, to_key=PyremoteRemoteSpawning),

        inj.bind(RemoteExecution, singleton=True),
    ]

    if (pf := remote_config.payload_file) is not None:
        lst.append(inj.bind(pf, to_key=RemoteExecutionPayloadFile))

    return inj.as_bindings(*lst)
