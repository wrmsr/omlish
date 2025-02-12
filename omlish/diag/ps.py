# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc
import os
import typing as ta

from ..lite.check import check
from ..lite.timeouts import Timeout
from ..subprocesses.run import SubprocessRun
from ..subprocesses.run import SubprocessRunnable
from ..subprocesses.run import SubprocessRunOutput
from ..subprocesses.sync import subprocesses


##


@dc.dataclass(frozen=True)
class PsItem:
    pid: int
    ppid: int
    cmd: str


@dc.dataclass(frozen=True)
class PsCommand(SubprocessRunnable):
    pid: ta.Optional[int] = None

    def make_run(self) -> SubprocessRun:
        return SubprocessRun.of(
            'ps',
            '-o', 'pid=,ppid=,command=',
            *([str(int(self.pid))] if self.pid is not None else []),

            check=True,
            stdout='pipe',
            stderr='devnull',
        )

    def handle_run_output(self, output: SubprocessRunOutput) -> PsItem:
        opid, ppid, cmd = check.not_none(output.stdout).decode().split(maxsplit=2)
        return PsItem(
            int(opid),
            int(ppid),
            cmd.strip(),
        )


##


def get_ps_item(pid: int, timeout: ta.Optional[Timeout] = None) -> PsItem:
    return PsCommand(pid).run(subprocesses, timeout=timeout)


def get_ps_lineage(pid: int, timeout: ta.Optional[Timeout] = None) -> ta.List[PsItem]:
    timeout = Timeout.of(timeout)
    ret: list[PsItem] = []
    while True:
        cur = get_ps_item(pid, timeout)
        if cur.ppid < 1:
            break
        ret.append(cur)
        pid = cur.ppid
    return ret


##


if __name__ == '__main__':
    def _main() -> None:
        print(get_ps_lineage(os.getpid()))

    _main()
