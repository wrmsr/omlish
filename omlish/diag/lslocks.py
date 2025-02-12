# ruff: noqa: UP006 UP007
# @omlish-lite
"""
https://github.com/util-linux/util-linux/blob/a4436c7bf07f98a6381c7dfa2ab3f9a415f9c479/misc-utils/lslocks.c
"""
import dataclasses as dc
import json
import typing as ta

from ..lite.check import check
from ..lite.marshal import OBJ_MARSHALER_FIELD_KEY
from ..lite.marshal import unmarshal_obj
from ..subprocesses.run import SubprocessRun
from ..subprocesses.run import SubprocessRunnable
from ..subprocesses.run import SubprocessRunOutput


##


@dc.dataclass(frozen=True)
class LslocksItem:
    """https://manpages.ubuntu.com/manpages/lunar/man8/lslocks.8.html"""

    command: str
    pid: int
    type: str  # POSIX | FLOCK | OFDLCK
    size: ta.Optional[int]
    mode: str  # READ | WRITE
    mandatory: bool = dc.field(metadata={OBJ_MARSHALER_FIELD_KEY: 'm'})
    start: int
    end: int
    path: str
    blocker: ta.Optional[int] = None


##


@dc.dataclass(frozen=True)
class LslocksCommand(SubprocessRunnable[ta.List[LslocksItem]]):
    pid: ta.Optional[int] = None
    no_inaccessible: bool = False

    def make_run(self) -> SubprocessRun:
        return SubprocessRun.of(
            'lslocks',
            '--json',
            '--bytes',
            '--notruncate',
            *(['--pid', str(self.pid)] if self.pid is not None else []),
            *(['--noinaccessible'] if self.no_inaccessible else []),

            check=True,
            stdout='pipe',
            stderr='devnull',
        )

    def handle_run_output(self, output: SubprocessRunOutput) -> ta.List[LslocksItem]:
        buf = check.not_none(output.stdout).decode().strip()
        if not buf:
            return []
        obj = json.loads(buf)
        return unmarshal_obj(obj['locks'], ta.List[LslocksItem])
