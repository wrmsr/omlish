# ruff: noqa: UP006 UP007 UP045
import errno
import os
import typing as ta

from omlish.logs.protocols import LoggerLike

from .ostypes import Pid
from .ostypes import Rc
from .signals import sig_name


##


def real_exit(code: Rc) -> None:
    os._exit(code)  # noqa


##


def decode_wait_status(sts: int) -> ta.Tuple[Rc, str]:
    """
    Decode the status returned by wait() or waitpid().

    Return a tuple (exitstatus, message) where exitstatus is the exit status, or -1 if the process was killed by a
    signal; and message is a message telling what happened. It is the caller's responsibility to display the message.
    """

    if os.WIFEXITED(sts):
        es = os.WEXITSTATUS(sts) & 0xffff
        msg = f'exit status {es}'
        return Rc(es), msg

    elif os.WIFSIGNALED(sts):
        sig = os.WTERMSIG(sts)
        msg = f'terminated by {sig_name(sig)}'
        if hasattr(os, 'WCOREDUMP'):
            iscore = os.WCOREDUMP(sts)
        else:
            iscore = bool(sts & 0x80)
        if iscore:
            msg += ' (core dumped)'
        return Rc(-1), msg

    else:
        msg = 'unknown termination cause 0x%04x' % sts  # noqa
        return Rc(-1), msg


##


class WaitedPid(ta.NamedTuple):
    pid: Pid
    sts: Rc


def waitpid(
        *,
        log: ta.Optional[LoggerLike] = None,
) -> ta.Optional[WaitedPid]:
    # Need pthread_sigmask here to avoid concurrent sigchld, but Python doesn't offer in Python < 3.4. There is
    # still a race condition here; we can get a sigchld while we're sitting in the waitpid call. However, AFAICT, if
    # waitpid is interrupted by SIGCHLD, as long as we call waitpid again (which happens every so often during the
    # normal course in the mainloop), we'll eventually reap the child that we tried to reap during the interrupted
    # call. At least on Linux, this appears to be true, or at least stopping 50 processes at once never left zombies
    # lying around.
    try:
        pid, sts = os.waitpid(-1, os.WNOHANG)

    except OSError as exc:
        code = exc.args[0]

        if code not in (errno.ECHILD, errno.EINTR):
            if log is not None:
                log.critical('waitpid error %r; a process may not be cleaned up properly', code)

        if code == errno.EINTR:
            if log is not None:
                log.debug('EINTR during reap')

        return None

    else:
        return WaitedPid(pid, sts)  # type: ignore
