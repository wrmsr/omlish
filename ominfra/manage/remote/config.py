# ruff: noqa: UP006 UP007
import dataclasses as dc
import typing as ta

from omlish.lite.pycharm import PycharmRemoteDebug


@dc.dataclass(frozen=True)
class RemoteConfig:
    payload_file: ta.Optional[str] = None

    set_pgid: bool = True

    deathsig: ta.Optional[str] = 'KILL'

    pycharm_remote_debug: ta.Optional[PycharmRemoteDebug] = None

    forward_logging: bool = True

    timebomb_delay_s: ta.Optional[float] = 60 * 60.

    heartbeat_interval_s: float = 3.
