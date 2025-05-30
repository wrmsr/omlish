import os
import typing as ta

from .. import dataclasses as dc
from .. import lang


if ta.TYPE_CHECKING:
    import psutil as _psutil
else:
    _psutil = lang.proxy_import('psutil')


##


@dc.dataclass(frozen=True)
class Times:
    user: float
    system: float
    children_user: float
    children_system: float
    elapsed: float


def times() -> Times:
    t = os.times()
    return Times(**{f.name: getattr(t, f.name) for f in dc.fields(Times)})


##


@dc.dataclass(frozen=True, kw_only=True)
class ProcStats:
    pid: int

    rss: int = dc.xfield(repr_fn=lambda i: f'{i:_}')


def get_psutil_procstats(pid: int | None = None) -> ProcStats:
    if pid is None:
        pid = os.getpid()

    proc = _psutil.Process(pid)
    mi = proc.memory_info()

    return ProcStats(
        pid=pid,

        rss=mi.rss,
    )
