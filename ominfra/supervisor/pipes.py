# ruff: noqa: UP006 UP007 UP045
import dataclasses as dc
import fcntl
import os
import typing as ta

from .utils.fds import close_fd
from .utils.fds import make_pipe
from .utils.ostypes import Fd


##


@dc.dataclass(frozen=True)
class ProcessPipes:
    child_stdin: ta.Optional[Fd] = None
    stdin: ta.Optional[Fd] = None

    stdout: ta.Optional[Fd] = None
    child_stdout: ta.Optional[Fd] = None

    stderr: ta.Optional[Fd] = None
    child_stderr: ta.Optional[Fd] = None

    def child_fds(self) -> ta.List[Fd]:
        return [fd for fd in [self.child_stdin, self.child_stdout, self.child_stderr] if fd is not None]

    def parent_fds(self) -> ta.List[Fd]:
        return [fd for fd in [self.stdin, self.stdout, self.stderr] if fd is not None]


def make_process_pipes(stderr=True) -> ProcessPipes:
    """
    Create pipes for parent to child stdin/stdout/stderr communications. Open fd in non-blocking mode so we can read
    them in the mainloop without blocking. If stderr is False, don't create a pipe for stderr.
    """

    pipes: ta.Dict[str, ta.Optional[Fd]] = {
        'child_stdin': None,
        'stdin': None,

        'stdout': None,
        'child_stdout': None,

        'stderr': None,
        'child_stderr': None,
    }

    try:
        pipes['child_stdin'], pipes['stdin'] = make_pipe()
        pipes['stdout'], pipes['child_stdout'] = make_pipe()

        if stderr:
            pipes['stderr'], pipes['child_stderr'] = make_pipe()

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


def close_pipes(pipes: ProcessPipes) -> None:
    close_parent_pipes(pipes)
    close_child_pipes(pipes)


def close_parent_pipes(pipes: ProcessPipes) -> None:
    for fd in pipes.parent_fds():
        close_fd(fd)


def close_child_pipes(pipes: ProcessPipes) -> None:
    for fd in pipes.child_fds():
        close_fd(fd)
