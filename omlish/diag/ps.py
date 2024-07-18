import dataclasses as dc
import os
import subprocess

from .. import lang


@dc.dataclass(frozen=True)
class PsItem:
    pid: int
    ppid: int
    cmd: str


def get_ps_item(pid: int, timeout: lang.Timeout | None = None) -> PsItem:
    timeout = lang.timeout(timeout)
    out = subprocess.check_output(
        ['ps', '-o', 'pid=,ppid=,command=', str(int(pid))],
        timeout=timeout.or_(None),
    ).decode().strip()
    opid, _, rest = out.partition(' ')
    ppid, _, cmd = rest.strip().partition(' ')
    return PsItem(
        int(opid),
        int(ppid),
        cmd.strip(),
    )


def get_ps_lineage(pid: int, timeout: lang.Timeout | None = None) -> list[PsItem]:
    timeout = lang.timeout(timeout)
    ret: list[PsItem] = []
    while True:
        cur = get_ps_item(pid, timeout)
        if cur.ppid < 1:
            break
        ret.append(cur)
        pid = cur.ppid
    return ret


def _main() -> None:
    print(get_ps_lineage(os.getpid()))


if __name__ == '__main__':
    _main()
