# NOTE: not '@omlish-lite' due to root level __init__ imports, but effectively lite.
import dataclasses as dc
import fcntl
import json
import os.path
import shutil
import sys
import time
import typing as ta


##


@dc.dataclass(frozen=True)
class CmdLogEntry:
    cmd: str
    pid: int
    ppid: int
    time: float
    cwd: str

    argv: ta.Sequence[str]
    env: ta.Mapping[str, str]


##


LOG_FILE_ENV_VAR: str = '_CMD_LOG_FILE'


def _main() -> None:
    cmd = os.path.basename(sys.argv[0])

    entry = CmdLogEntry(
        cmd=cmd,
        pid=os.getpid(),
        ppid=os.getppid(),
        time=time.time(),
        cwd=os.getcwd(),

        argv=sys.argv,
        env=dict(os.environ),
    )

    entry_json = json.dumps(dc.asdict(entry), separators=(',', ':'), indent=None)

    log_file = os.environ[LOG_FILE_ENV_VAR]
    fd = os.open(log_file, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
    fcntl.flock(fd, fcntl.LOCK_EX)
    os.write(fd, entry_json.encode() + b'\n')
    os.close(fd)

    u_ap = None  # type: str | None
    self_ap = os.path.abspath(os.path.realpath(__file__))
    for p in os.environ.get('PATH', '').split(os.pathsep):
        if (p_cmd := shutil.which(cmd, path=p)) is None:
            continue
        p_ap = os.path.abspath(os.path.realpath(p_cmd))
        if p_ap == self_ap:
            continue
        u_ap = p_ap
        break

    if u_ap is None:
        raise FileNotFoundError(cmd)

    os.execl(u_ap, cmd, *sys.argv[1:])


if __name__ == '__main__':
    _main()
