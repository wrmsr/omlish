# ruff: noqa: UP006 UP007
import dataclasses as dc
import typing as ta

from omlish.lite.pycharm import PycharmRemoteDebug

from .spawning import RemoteSpawning


@dc.dataclass(frozen=True)
class RemoteConfig:
    spawning: RemoteSpawning.Options = RemoteSpawning.Options()

    pycharm_remote_debug: ta.Optional[PycharmRemoteDebug] = None
