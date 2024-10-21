# ruff: noqa: UP006 UP007
import errno
import os
import signal
import sys
import tempfile
import types
import typing as ta


T = ta.TypeVar('T')


def as_bytes(s: ta.Union[str, bytes], encoding: str = 'utf8') -> bytes:
    if isinstance(s, bytes):
        return s
    else:
        return s.encode(encoding)


def as_string(s: ta.Union[str, bytes], encoding='utf8') -> str:
    if isinstance(s, str):
        return s
    else:
        return s.decode(encoding)


def compact_traceback() -> ta.Tuple[
    ta.Tuple[str, str, int],
    ta.Type[BaseException],
    BaseException,
    types.TracebackType,
]:
    t, v, tb = sys.exc_info()
    tbinfo = []
    if not tb:
        raise RuntimeError('No traceback')
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


def find_prefix_at_end(haystack: bytes, needle: bytes) -> int:
    l = len(needle) - 1
    while l and not haystack.endswith(needle[:l]):
        l -= 1
    return l


class ExitNow(Exception):  # noqa
    pass


##


def decode_wait_status(sts: int) -> ta.Tuple[int, str]:
    """
    Decode the status returned by wait() or waitpid().

    Return a tuple (exitstatus, message) where exitstatus is the exit status, or -1 if the process was killed by a
    signal; and message is a message telling what happened.  It is the caller's responsibility to display the message.
    """
    if os.WIFEXITED(sts):
        es = os.WEXITSTATUS(sts) & 0xffff
        msg = f'exit status {es}'
        return es, msg
    elif os.WIFSIGNALED(sts):
        sig = os.WTERMSIG(sts)
        msg = f'terminated by {signame(sig)}'
        if hasattr(os, 'WCOREDUMP'):
            iscore = os.WCOREDUMP(sts)
        else:
            iscore = bool(sts & 0x80)
        if iscore:
            msg += ' (core dumped)'
        return -1, msg
    else:
        msg = 'unknown termination cause 0x%04x' % sts  # noqa
        return -1, msg


_signames: ta.Optional[ta.Mapping[int, str]] = None


def signame(sig: int) -> str:
    global _signames
    if _signames is None:
        _signames = _init_signames()
    return _signames.get(sig) or 'signal %d' % sig


def _init_signames() -> ta.Dict[int, str]:
    d = {}
    for k, v in signal.__dict__.items():
        k_startswith = getattr(k, 'startswith', None)
        if k_startswith is None:
            continue
        if k_startswith('SIG') and not k_startswith('SIG_'):
            d[v] = k
    return d


class SignalReceiver:
    def __init__(self) -> None:
        super().__init__()
        self._signals_recvd: ta.List[int] = []

    def receive(self, sig: int, frame: ta.Any) -> None:
        if sig not in self._signals_recvd:
            self._signals_recvd.append(sig)

    def install(self, *sigs: int) -> None:
        for sig in sigs:
            signal.signal(sig, self.receive)

    def get_signal(self) -> ta.Optional[int]:
        if self._signals_recvd:
            sig = self._signals_recvd.pop(0)
        else:
            sig = None
        return sig


def readfd(fd: int) -> bytes:
    try:
        data = os.read(fd, 2 << 16)  # 128K
    except OSError as why:
        if why.args[0] not in (errno.EWOULDBLOCK, errno.EBADF, errno.EINTR):
            raise
        data = b''
    return data


def try_unlink(path: str) -> bool:
    try:
        os.unlink(path)
    except OSError:
        return False
    return True


def close_fd(fd: int) -> bool:
    try:
        os.close(fd)
    except OSError:
        return False
    return True


def mktempfile(suffix: str, prefix: str, dir: str) -> str:  # noqa
    fd, filename = tempfile.mkstemp(suffix, prefix, dir)
    os.close(fd)
    return filename


def real_exit(code: int) -> None:
    os._exit(code)  # noqa


def get_path() -> ta.Sequence[str]:
    """Return a list corresponding to $PATH, or a default."""
    path = ['/bin', '/usr/bin', '/usr/local/bin']
    if 'PATH' in os.environ:
        p = os.environ['PATH']
        if p:
            path = p.split(os.pathsep)
    return path


def normalize_path(v: str) -> str:
    return os.path.normpath(os.path.abspath(os.path.expanduser(v)))


ANSI_ESCAPE_BEGIN = b'\x1b['
ANSI_TERMINATORS = (b'H', b'f', b'A', b'B', b'C', b'D', b'R', b's', b'u', b'J', b'K', b'h', b'l', b'p', b'm')


def strip_escapes(s):
    """Remove all ANSI color escapes from the given string."""
    result = b''
    show = 1
    i = 0
    l = len(s)
    while i < l:
        if show == 0 and s[i:i + 1] in ANSI_TERMINATORS:
            show = 1
        elif show:
            n = s.find(ANSI_ESCAPE_BEGIN, i)
            if n == -1:
                return result + s[i:]
            else:
                result = result + s[i:n]
                i = n
                show = 0
        i += 1
    return result
