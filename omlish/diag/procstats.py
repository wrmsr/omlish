import dataclasses as dc
import os
import typing as ta

from .. import lang


if ta.TYPE_CHECKING:
    import psutil as _psutil
else:
    _psutil = lang.proxy_import('psutil')


@dc.dataclass(frozen=True, kw_only=True)
class ProcStats:
    pid: int

    rss: int


def get_psutil_procstats(pid: int | None = None) -> ProcStats:
    if pid is None:
        pid = os.getpid()

    proc = _psutil.Process(pid)
    mi = proc.memory_info()

    return ProcStats(
        pid=pid,

        rss=mi.rss,
    )
