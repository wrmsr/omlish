# ruff: noqa: UP006 UP007
import dataclasses as dc
import fcntl
import os
import typing as ta

from .utils import close_fd


@dc.dataclass(frozen=True)
class ProcessPipes:
    child_stdin: ta.Optional[int] = None
    stdin: ta.Optional[int] = None

    stdout: ta.Optional[int] = None
    child_stdout: ta.Optional[int] = None

    stderr: ta.Optional[int] = None
    child_stderr: ta.Optional[int] = None

    def as_dict(self) -> ta.Mapping[str, int]:
        return dc.asdict(self)


def make_process_pipes(stderr=True) -> ProcessPipes:
    """
    Create pipes for parent to child stdin/stdout/stderr communications.  Open fd in non-blocking mode so we can
    read them in the mainloop without blocking.  If stderr is False, don't create a pipe for stderr.
    """

    pipes: ta.Dict[str, ta.Optional[int]] = {
        'child_stdin': None,
        'stdin': None,

        'stdout': None,
        'child_stdout': None,

        'stderr': None,
        'child_stderr': None,
    }

    try:
        pipes['child_stdin'], pipes['stdin'] = os.pipe()
        pipes['stdout'], pipes['child_stdout'] = os.pipe()

        if stderr:
            pipes['stderr'], pipes['child_stderr'] = os.pipe()

        for fd in (
                pipes['stdout'],
                pipes['stderr'],
                pipes['stdin'],
        ):
            if fd is not None:
                flags = fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NDELAY
                fcntl.fcntl(fd, fcntl.F_SETFL, flags)

        return ProcessPipes(**pipes)

    except OSError:
        for fd in pipes.values():
            if fd is not None:
                close_fd(fd)

        raise


def close_parent_pipes(pipes: ProcessPipes) -> None:
    for name in (
            'stdin',
            'stdout',
            'stderr',
    ):
        fd = getattr(pipes, name)
        if fd is not None:
            close_fd(fd)


def close_child_pipes(pipes: ProcessPipes) -> None:
    for name in (
            'child_stdin',
            'child_stdout',
            'child_stderr',
    ):
        fd = getattr(pipes, name)
        if fd is not None:
            close_fd(fd)
