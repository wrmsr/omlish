import dataclasses as dc
import os
import subprocess

from omlish import lang


@dc.dataclass(frozen=True)
class PsItem:
    pid: int
    ppid: int
    exe: str


def get_ps_item(pid: int, timeout: lang.Timeout | None = None) -> PsItem:
    timeout = lang.timeout(timeout)
    out = subprocess.check_output(
        ['ps', '-o', 'pid=,ppid=,command=', str(int(pid))],
        timeout=timeout.or_(None),
    )
    print(out)


def _main():
    get_ps_item(os.getpid())


if __name__ == '__main__':
    _main()
