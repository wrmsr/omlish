# ruff: noqa: UP006 UP007
import dataclasses as dc
import typing as ta

from omlish.lite.pycharm import PycharmRemoteDebug


@dc.dataclass(frozen=True)
class RemoteConfig:
    payload_file: ta.Optional[str] = None

    pycharm_remote_debug: ta.Optional[PycharmRemoteDebug] = None

    forward_logging: bool = True
