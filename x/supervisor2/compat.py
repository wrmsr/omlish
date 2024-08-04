import errno
import importlib.metadata
import io
import os
import signal
import sys
import typing as ta


def as_bytes(s, encoding='utf8'):
    if isinstance(s, bytes):
        return s
    else:
        return s.encode(encoding)


def as_string(s, encoding='utf8'):
    if isinstance(s, str):
        return s
    else:
        return s.decode(encoding)


def is_text_stream(stream):
    return isinstance(stream, io.TextIOBase)


def import_spec(spec):
    return importlib.metadata.EntryPoint(None, spec, None).load()  # noqa


def compact_traceback():
    t, v, tb = sys.exc_info()
    tbinfo = []
    assert tb  # Must have a traceback
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
    info = ' '.join(['[%s|%s|%s]' % x for x in tbinfo])
    return (file, function, line), t, v, info


def find_prefix_at_end(haystack: str, needle: str) -> int:
    l = len(needle) - 1
    while l and not haystack.endswith(needle[:l]):
        l -= 1
    return l


class ExitNow(Exception):
    pass


def expand(s: str, expansions: ta.Any, name: str) -> str:
    try:
        return s % expansions
    except KeyError as ex:
        available = list(expansions.keys())
        available.sort()
        raise ValueError(
            'Format string %r for %r contains names (%s) which cannot be '
            'expanded. Available names: %s' % (s, name, str(ex), ', '.join(available)))
    except Exception as ex:
        raise ValueError('Format string %r for %r is badly formatted: %s' % (s, name, str(ex)))


##


def decode_wait_status(sts):
    """
    Decode the status returned by wait() or waitpid().

    Return a tuple (exitstatus, message) where exitstatus is the exit status, or -1 if the process was killed by a
    signal; and message is a message telling what happened.  It is the caller's responsibility to display the message.
    """
    if os.WIFEXITED(sts):
        es = os.WEXITSTATUS(sts) & 0xffff
        msg = 'exit status %s' % es
        return es, msg
    elif os.WIFSIGNALED(sts):
        sig = os.WTERMSIG(sts)
        msg = 'terminated by %s' % signame(sig)
        if hasattr(os, 'WCOREDUMP'):
            iscore = os.WCOREDUMP(sts)
        else:
            iscore = sts & 0x80
        if iscore:
            msg += ' (core dumped)'
        return -1, msg
    else:
        msg = 'unknown termination cause 0x%04x' % sts
        return -1, msg


_signames = None


def signame(sig):
    """
    Return a symbolic name for a signal.

    Return "signal NNN" if there is no corresponding SIG name in the signal module.
    """

    if _signames is None:
        _init_signames()
    return _signames.get(sig) or 'signal %d' % sig


def _init_signames():
    global _signames
    d = {}
    for k, v in signal.__dict__.items():
        k_startswith = getattr(k, 'startswith', None)
        if k_startswith is None:
            continue
        if k_startswith('SIG') and not k_startswith('SIG_'):
            d[v] = k
    _signames = d


class SignalReceiver:
    def __init__(self):
        self._signals_recvd = []

    def receive(self, sig, frame):
        if sig not in self._signals_recvd:
            self._signals_recvd.append(sig)

    def get_signal(self) -> int | None:
        if self._signals_recvd:
            sig = self._signals_recvd.pop(0)
        else:
            sig = None
        return sig


def readfd(self, fd: int) -> bytes:
    try:
        data = os.read(fd, 2 << 16)  # 128K
    except OSError as why:
        if why.args[0] not in (errno.EWOULDBLOCK, errno.EBADF, errno.EINTR):
            raise
        data = b''
    return data
