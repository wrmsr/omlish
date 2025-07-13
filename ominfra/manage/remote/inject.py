# ruff: noqa: UP006 UP007 UP045
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from .config import RemoteConfig
from .connection import InProcessRemoteExecutionConnector
from .connection import PyremoteRemoteExecutionConnector
from .payload import RemoteExecutionPayloadFile
from .spawning import RemoteSpawning
from .spawning import SubprocessRemoteSpawning


##


def bind_remote(
        *,
        remote_config: RemoteConfig,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(remote_config),

        inj.bind(SubprocessRemoteSpawning, singleton=True),
        inj.bind(RemoteSpawning, to_key=SubprocessRemoteSpawning),

        inj.bind(PyremoteRemoteExecutionConnector, singleton=True),
        inj.bind(InProcessRemoteExecutionConnector, singleton=True),
    ]

    #

    if (pf := remote_config.payload_file) is not None:
        lst.append(inj.bind(pf, key=RemoteExecutionPayloadFile))

    #

    return inj.as_bindings(*lst)
