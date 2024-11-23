# ruff: noqa: UP006 UP007
import os
import sys
import types
import typing as ta

from .ostypes import Rc
from .signals import sig_name


##


def compact_traceback() -> ta.Tuple[
    ta.Tuple[str, str, int],
    ta.Type[BaseException],
    BaseException,
    types.TracebackType,
]:
    t, v, tb = sys.exc_info()
    if not tb:
        raise RuntimeError('No traceback')

    tbinfo = []
    while tb:
        tbinfo.append((
            tb.tb_frame.f_code.co_filename,
            tb.tb_frame.f_code.co_name,
            str(tb.tb_lineno),
        ))
        tb = tb.tb_next

    # just to be safe
    del tb

    file, function, line = tbinfo[-1]
    info = ' '.join(['[%s|%s|%s]' % x for x in tbinfo])  # noqa
    return (file, function, line), t, v, info  # type: ignore


##


class ExitNow(Exception):  # noqa
    pass


def real_exit(code: Rc) -> None:
    os._exit(code)  # noqa


##


def decode_wait_status(sts: int) -> ta.Tuple[Rc, str]:
    """
    Decode the status returned by wait() or waitpid().

    Return a tuple (exitstatus, message) where exitstatus is the exit status, or -1 if the process was killed by a
    signal; and message is a message telling what happened.  It is the caller's responsibility to display the message.
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


def timeslice(period: int, when: float) -> int:
    return int(when - (when % period))
