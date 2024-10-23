#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omlish-lite
# @omlish-script
# @omlish-amalg-output ../supervisor/supervisor.py
# ruff: noqa: N802 UP006 UP007 UP036
import abc
import contextlib
import dataclasses as dc
import datetime
import errno
import fcntl
import functools
import grp
import json
import logging
import os
import pwd
import re
import resource
import select
import shlex
import signal
import stat
import sys
import tempfile
import threading
import time
import traceback
import types
import typing as ta
import warnings


########################################


if sys.version_info < (3, 8):
    raise OSError(
        f'Requires python (3, 8), got {sys.version_info} from {sys.executable}')  # noqa


########################################


# ../compat.py
T = ta.TypeVar('T')

# ../states.py
ProcessState = int  # ta.TypeAlias
SupervisorState = int  # ta.TypeAlias


########################################
# ../compat.py


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


########################################
# ../datatypes.py


class Automatic:
    pass


class Syslog:
    """TODO deprecated; remove this special 'syslog' filename in the future"""


LOGFILE_NONES = ('none', 'off', None)
LOGFILE_AUTOS = (Automatic, 'auto')
LOGFILE_SYSLOGS = (Syslog, 'syslog')


def logfile_name(val):
    if hasattr(val, 'lower'):
        coerced = val.lower()
    else:
        coerced = val

    if coerced in LOGFILE_NONES:
        return None
    elif coerced in LOGFILE_AUTOS:
        return Automatic
    elif coerced in LOGFILE_SYSLOGS:
        return Syslog
    else:
        return existing_dirpath(val)


def name_to_uid(name: str) -> int:
    try:
        uid = int(name)
    except ValueError:
        try:
            pwdrec = pwd.getpwnam(name)
        except KeyError:
            raise ValueError(f'Invalid user name {name}')  # noqa
        uid = pwdrec[2]
    else:
        try:
            pwd.getpwuid(uid)  # check if uid is valid
        except KeyError:
            raise ValueError(f'Invalid user id {name}')  # noqa
    return uid


def name_to_gid(name: str) -> int:
    try:
        gid = int(name)
    except ValueError:
        try:
            grprec = grp.getgrnam(name)
        except KeyError:
            raise ValueError(f'Invalid group name {name}')  # noqa
        gid = grprec[2]
    else:
        try:
            grp.getgrgid(gid)  # check if gid is valid
        except KeyError:
            raise ValueError(f'Invalid group id {name}')  # noqa
    return gid


def gid_for_uid(uid: int) -> int:
    pwrec = pwd.getpwuid(uid)
    return pwrec[3]


def octal_type(arg: ta.Union[str, int]) -> int:
    if isinstance(arg, int):
        return arg
    try:
        return int(arg, 8)
    except (TypeError, ValueError):
        raise ValueError(f'{arg} can not be converted to an octal type')  # noqa


def existing_directory(v: str) -> str:
    nv = os.path.expanduser(v)
    if os.path.isdir(nv):
        return nv
    raise ValueError(f'{v} is not an existing directory')


def existing_dirpath(v: str) -> str:
    nv = os.path.expanduser(v)
    dir = os.path.dirname(nv)  # noqa
    if not dir:
        # relative pathname with no directory component
        return nv
    if os.path.isdir(dir):
        return nv
    raise ValueError(f'The directory named as part of the path {v} does not exist')


def logging_level(value: ta.Union[str, int]) -> int:
    if isinstance(value, int):
        return value
    s = str(value).lower()
    level = logging.getLevelNamesMapping().get(s.upper())
    if level is None:
        raise ValueError(f'bad logging level name {value!r}')
    return level


class SuffixMultiplier:
    # d is a dictionary of suffixes to integer multipliers.  If no suffixes match, default is the multiplier.  Matches
    # are case insensitive.  Return values are in the fundamental unit.
    def __init__(self, d, default=1):
        super().__init__()
        self._d = d
        self._default = default
        # all keys must be the same size
        self._keysz = None
        for k in d:
            if self._keysz is None:
                self._keysz = len(k)
            elif self._keysz != len(k):  # type: ignore
                raise ValueError(k)

    def __call__(self, v: ta.Union[str, int]) -> int:
        if isinstance(v, int):
            return v
        v = v.lower()
        for s, m in self._d.items():
            if v[-self._keysz:] == s:  # type: ignore
                return int(v[:-self._keysz]) * m  # type: ignore
        return int(v) * self._default


byte_size = SuffixMultiplier({
    'kb': 1024,
    'mb': 1024 * 1024,
    'gb': 1024 * 1024 * 1024,
})


# all valid signal numbers
SIGNUMS = [getattr(signal, k) for k in dir(signal) if k.startswith('SIG')]


def signal_number(value: ta.Union[int, str]) -> int:
    try:
        num = int(value)
    except (ValueError, TypeError):
        name = value.strip().upper()  # type: ignore
        if not name.startswith('SIG'):
            name = f'SIG{name}'
        num = getattr(signal, name, None)  # type: ignore
        if num is None:
            raise ValueError(f'value {value!r} is not a valid signal name')  # noqa
    if num not in SIGNUMS:
        raise ValueError(f'value {value!r} is not a valid signal number')
    return num


class RestartWhenExitUnexpected:
    pass


class RestartUnconditionally:
    pass


########################################
# ../exceptions.py


class ProcessError(Exception):
    """ Specialized exceptions used when attempting to start a process """


class BadCommandError(ProcessError):
    """ Indicates the command could not be parsed properly. """


class NotExecutableError(ProcessError):
    """ Indicates that the filespec cannot be executed because its path
    resolves to a file which is not executable, or which is a directory. """


class NotFoundError(ProcessError):
    """ Indicates that the filespec cannot be executed because it could not be found """


class NoPermissionError(ProcessError):
    """
    Indicates that the file cannot be executed because the supervisor process does not possess the appropriate UNIX
    filesystem permission to execute the file.
    """


########################################
# ../poller.py


log = logging.getLogger(__name__)


class BasePoller(abc.ABC):

    def __init__(self) -> None:
        super().__init__()

    @abc.abstractmethod
    def register_readable(self, fd: int) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def register_writable(self, fd: int) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def unregister_readable(self, fd: int) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def unregister_writable(self, fd: int) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def poll(self, timeout: ta.Optional[float]) -> ta.Tuple[ta.List[int], ta.List[int]]:
        raise NotImplementedError

    def before_daemonize(self) -> None:  # noqa
        pass

    def after_daemonize(self) -> None:  # noqa
        pass

    def close(self) -> None:  # noqa
        pass


class SelectPoller(BasePoller):

    def __init__(self) -> None:
        super().__init__()

        self._readables: ta.Set[int] = set()
        self._writables: ta.Set[int] = set()

    def register_readable(self, fd: int) -> None:
        self._readables.add(fd)

    def register_writable(self, fd: int) -> None:
        self._writables.add(fd)

    def unregister_readable(self, fd: int) -> None:
        self._readables.discard(fd)

    def unregister_writable(self, fd: int) -> None:
        self._writables.discard(fd)

    def unregister_all(self) -> None:
        self._readables.clear()
        self._writables.clear()

    def poll(self, timeout: ta.Optional[float]) -> ta.Tuple[ta.List[int], ta.List[int]]:
        try:
            r, w, x = select.select(
                self._readables,
                self._writables,
                [], timeout,
            )
        except OSError as err:
            if err.args[0] == errno.EINTR:
                log.debug('EINTR encountered in poll')
                return [], []
            if err.args[0] == errno.EBADF:
                log.debug('EBADF encountered in poll')
                self.unregister_all()
                return [], []
            raise
        return r, w


class PollPoller(BasePoller):
    _READ = select.POLLIN | select.POLLPRI | select.POLLHUP
    _WRITE = select.POLLOUT

    def __init__(self) -> None:
        super().__init__()

        self._poller = select.poll()
        self._readables: set[int] = set()
        self._writables: set[int] = set()

    def register_readable(self, fd: int) -> None:
        self._poller.register(fd, self._READ)
        self._readables.add(fd)

    def register_writable(self, fd: int) -> None:
        self._poller.register(fd, self._WRITE)
        self._writables.add(fd)

    def unregister_readable(self, fd: int) -> None:
        self._readables.discard(fd)
        self._poller.unregister(fd)
        if fd in self._writables:
            self._poller.register(fd, self._WRITE)

    def unregister_writable(self, fd: int) -> None:
        self._writables.discard(fd)
        self._poller.unregister(fd)
        if fd in self._readables:
            self._poller.register(fd, self._READ)

    def poll(self, timeout: ta.Optional[float]) -> ta.Tuple[ta.List[int], ta.List[int]]:
        fds = self._poll_fds(timeout)  # type: ignore
        readables, writables = [], []
        for fd, eventmask in fds:
            if self._ignore_invalid(fd, eventmask):
                continue
            if eventmask & self._READ:
                readables.append(fd)
            if eventmask & self._WRITE:
                writables.append(fd)
        return readables, writables

    def _poll_fds(self, timeout: float) -> ta.List[ta.Tuple[int, int]]:
        try:
            return self._poller.poll(timeout * 1000)
        except OSError as err:
            if err.args[0] == errno.EINTR:
                log.debug('EINTR encountered in poll')
                return []
            raise

    def _ignore_invalid(self, fd: int, eventmask: int) -> bool:
        if eventmask & select.POLLNVAL:
            # POLLNVAL means `fd` value is invalid, not open. When a process quits it's `fd`s are closed so there is no
            # more reason to keep this `fd` registered If the process restarts it's `fd`s are registered again.
            self._poller.unregister(fd)
            self._readables.discard(fd)
            self._writables.discard(fd)
            return True
        return False


if sys.platform == 'darwin' or sys.platform.startswith('freebsd'):
    class KqueuePoller(BasePoller):
        max_events = 1000

        def __init__(self) -> None:
            super().__init__()

            self._kqueue: ta.Optional[ta.Any] = select.kqueue()
            self._readables: set[int] = set()
            self._writables: set[int] = set()

        def register_readable(self, fd: int) -> None:
            self._readables.add(fd)
            kevent = select.kevent(fd, filter=select.KQ_FILTER_READ, flags=select.KQ_EV_ADD)
            self._kqueue_control(fd, kevent)

        def register_writable(self, fd: int) -> None:
            self._writables.add(fd)
            kevent = select.kevent(fd, filter=select.KQ_FILTER_WRITE, flags=select.KQ_EV_ADD)
            self._kqueue_control(fd, kevent)

        def unregister_readable(self, fd: int) -> None:
            kevent = select.kevent(fd, filter=select.KQ_FILTER_READ, flags=select.KQ_EV_DELETE)
            self._readables.discard(fd)
            self._kqueue_control(fd, kevent)

        def unregister_writable(self, fd: int) -> None:
            kevent = select.kevent(fd, filter=select.KQ_FILTER_WRITE, flags=select.KQ_EV_DELETE)
            self._writables.discard(fd)
            self._kqueue_control(fd, kevent)

        def _kqueue_control(self, fd: int, kevent: 'select.kevent') -> None:
            try:
                self._kqueue.control([kevent], 0)  # type: ignore
            except OSError as error:
                if error.errno == errno.EBADF:
                    log.debug('EBADF encountered in kqueue. Invalid file descriptor %s', fd)
                else:
                    raise

        def poll(self, timeout: ta.Optional[float]) -> ta.Tuple[ta.List[int], ta.List[int]]:
            readables, writables = [], []  # type: ignore

            try:
                kevents = self._kqueue.control(None, self.max_events, timeout)  # type: ignore
            except OSError as error:
                if error.errno == errno.EINTR:
                    log.debug('EINTR encountered in poll')
                    return readables, writables
                raise

            for kevent in kevents:
                if kevent.filter == select.KQ_FILTER_READ:
                    readables.append(kevent.ident)
                if kevent.filter == select.KQ_FILTER_WRITE:
                    writables.append(kevent.ident)

            return readables, writables

        def before_daemonize(self) -> None:
            self.close()

        def after_daemonize(self) -> None:
            self._kqueue = select.kqueue()
            for fd in self._readables:
                self.register_readable(fd)
            for fd in self._writables:
                self.register_writable(fd)

        def close(self) -> None:
            self._kqueue.close()  # type: ignore
            self._kqueue = None

else:
    KqueuePoller = None


Poller: ta.Type[BasePoller]
if (
        sys.platform == 'darwin' or sys.platform.startswith('freebsd') and
        hasattr(select, 'kqueue') and KqueuePoller is not None
):
    Poller = KqueuePoller
elif hasattr(select, 'poll'):
    Poller = PollPoller
else:
    Poller = SelectPoller


########################################
# ../../../omlish/lite/check.py


def check_isinstance(v: T, spec: ta.Union[ta.Type[T], tuple]) -> T:
    if not isinstance(v, spec):
        raise TypeError(v)
    return v


def check_not_isinstance(v: T, spec: ta.Union[type, tuple]) -> T:
    if isinstance(v, spec):
        raise TypeError(v)
    return v


def check_not_none(v: ta.Optional[T]) -> T:
    if v is None:
        raise ValueError
    return v


def check_not(v: ta.Any) -> None:
    if v:
        raise ValueError(v)
    return v


def check_non_empty_str(v: ta.Optional[str]) -> str:
    if not v:
        raise ValueError
    return v


def check_state(v: bool, msg: str = 'Illegal state') -> None:
    if not v:
        raise ValueError(msg)


def check_equal(l: T, r: T) -> T:
    if l != r:
        raise ValueError(l, r)
    return l


def check_not_equal(l: T, r: T) -> T:
    if l == r:
        raise ValueError(l, r)
    return l


def check_single(vs: ta.Iterable[T]) -> T:
    [v] = vs
    return v


########################################
# ../../../omlish/lite/json.py


##


JSON_PRETTY_INDENT = 2

JSON_PRETTY_KWARGS: ta.Mapping[str, ta.Any] = dict(
    indent=JSON_PRETTY_INDENT,
)

json_dump_pretty: ta.Callable[..., bytes] = functools.partial(json.dump, **JSON_PRETTY_KWARGS)  # type: ignore
json_dumps_pretty: ta.Callable[..., str] = functools.partial(json.dumps, **JSON_PRETTY_KWARGS)


##


JSON_COMPACT_SEPARATORS = (',', ':')

JSON_COMPACT_KWARGS: ta.Mapping[str, ta.Any] = dict(
    indent=None,
    separators=JSON_COMPACT_SEPARATORS,
)

json_dump_compact: ta.Callable[..., bytes] = functools.partial(json.dump, **JSON_COMPACT_KWARGS)  # type: ignore
json_dumps_compact: ta.Callable[..., str] = functools.partial(json.dumps, **JSON_COMPACT_KWARGS)


########################################
# ../configs.py


@dc.dataclass(frozen=True)
class ServerConfig:
    user: ta.Optional[str] = None
    nodaemon: bool = False
    umask: int = 0o22
    directory: ta.Optional[str] = None
    logfile: str = 'supervisord.log'
    logfile_maxbytes: int = 50 * 1024 * 1024
    logfile_backups: int = 10
    loglevel: int = logging.INFO
    pidfile: str = 'supervisord.pid'
    identifier: str = 'supervisor'
    child_logdir: str = '/dev/null'
    minfds: int = 1024
    minprocs: int = 200
    nocleanup: bool = False
    strip_ansi: bool = False
    silent: bool = False

    groups: ta.Optional[ta.Sequence['ProcessGroupConfig']] = None

    @classmethod
    def new(
            cls,
            umask: ta.Union[int, str] = 0o22,
            directory: ta.Optional[str] = None,
            logfile: str = 'supervisord.log',
            logfile_maxbytes: ta.Union[int, str] = 50 * 1024 * 1024,
            loglevel: ta.Union[int, str] = logging.INFO,
            pidfile: str = 'supervisord.pid',
            child_logdir: ta.Optional[str] = None,
            **kwargs: ta.Any,
    ) -> 'ServerConfig':
        return cls(
            umask=octal_type(umask),
            directory=existing_directory(directory) if directory is not None else None,
            logfile=existing_dirpath(logfile),
            logfile_maxbytes=byte_size(logfile_maxbytes),
            loglevel=logging_level(loglevel),
            pidfile=existing_dirpath(pidfile),
            child_logdir=child_logdir if child_logdir else tempfile.gettempdir(),
            **kwargs,
        )


@dc.dataclass(frozen=True)
class ProcessGroupConfig:
    name: str

    priority: int = 999

    processes: ta.Optional[ta.Sequence['ProcessConfig']] = None


@dc.dataclass(frozen=True)
class ProcessConfig:
    name: str
    command: str

    uid: ta.Optional[int] = None
    directory: ta.Optional[str] = None
    umask: ta.Optional[int] = None
    priority: int = 999

    autostart: bool = True
    autorestart: str = 'unexpected'

    startsecs: int = 1
    startretries: int = 3

    numprocs: int = 1
    numprocs_start: int = 0

    @dc.dataclass(frozen=True)
    class Log:
        file: ta.Optional[str] = None
        capture_maxbytes: ta.Optional[int] = None
        events_enabled: bool = False
        syslog: bool = False
        backups: ta.Optional[int] = None
        maxbytes: ta.Optional[int] = None

    stdout: Log = Log()
    stderr: Log = Log()

    stopsignal: int = signal.SIGTERM
    stopwaitsecs: int = 10
    stopasgroup: bool = False

    killasgroup: bool = False

    exitcodes: ta.Iterable[int] = (0,)

    redirect_stderr: bool = False

    environment: ta.Optional[ta.Mapping[str, str]] = None


########################################
# ../states.py


##


def _names_by_code(states: ta.Any) -> ta.Dict[int, str]:
    d = {}
    for name in states.__dict__:
        if not name.startswith('__'):
            code = getattr(states, name)
            d[code] = name
    return d


##


class ProcessStates:
    STOPPED = 0
    STARTING = 10
    RUNNING = 20
    BACKOFF = 30
    STOPPING = 40
    EXITED = 100
    FATAL = 200
    UNKNOWN = 1000


STOPPED_STATES = (
    ProcessStates.STOPPED,
    ProcessStates.EXITED,
    ProcessStates.FATAL,
    ProcessStates.UNKNOWN,
)

RUNNING_STATES = (
    ProcessStates.RUNNING,
    ProcessStates.BACKOFF,
    ProcessStates.STARTING,
)

SIGNALLABLE_STATES = (
    ProcessStates.RUNNING,
    ProcessStates.STARTING,
    ProcessStates.STOPPING,
)


_process_states_by_code = _names_by_code(ProcessStates)


def get_process_state_description(code: ProcessState) -> str:
    return check_not_none(_process_states_by_code.get(code))


##


class SupervisorStates:
    FATAL = 2
    RUNNING = 1
    RESTARTING = 0
    SHUTDOWN = -1


_supervisor_states_by_code = _names_by_code(SupervisorStates)


def get_supervisor_state_description(code: SupervisorState) -> str:
    return check_not_none(_supervisor_states_by_code.get(code))


########################################
# ../../../omlish/lite/logs.py
"""
TODO:
 - translate json keys
 - debug
"""


log = logging.getLogger(__name__)


##


class TidLogFilter(logging.Filter):

    def filter(self, record):
        record.tid = threading.get_native_id()
        return True


##


class JsonLogFormatter(logging.Formatter):

    KEYS: ta.Mapping[str, bool] = {
        'name': False,
        'msg': False,
        'args': False,
        'levelname': False,
        'levelno': False,
        'pathname': False,
        'filename': False,
        'module': False,
        'exc_info': True,
        'exc_text': True,
        'stack_info': True,
        'lineno': False,
        'funcName': False,
        'created': False,
        'msecs': False,
        'relativeCreated': False,
        'thread': False,
        'threadName': False,
        'processName': False,
        'process': False,
    }

    def format(self, record: logging.LogRecord) -> str:
        dct = {
            k: v
            for k, o in self.KEYS.items()
            for v in [getattr(record, k)]
            if not (o and v is None)
        }
        return json_dumps_compact(dct)


##


STANDARD_LOG_FORMAT_PARTS = [
    ('asctime', '%(asctime)-15s'),
    ('process', 'pid=%(process)-6s'),
    ('thread', 'tid=%(thread)x'),
    ('levelname', '%(levelname)s'),
    ('name', '%(name)s'),
    ('separator', '::'),
    ('message', '%(message)s'),
]


class StandardLogFormatter(logging.Formatter):

    @staticmethod
    def build_log_format(parts: ta.Iterable[ta.Tuple[str, str]]) -> str:
        return ' '.join(v for k, v in parts)

    converter = datetime.datetime.fromtimestamp  # type: ignore

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)  # type: ignore
        if datefmt:
            return ct.strftime(datefmt)  # noqa
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")  # noqa
            return '%s.%03d' % (t, record.msecs)


##


class ProxyLogFilterer(logging.Filterer):
    def __init__(self, underlying: logging.Filterer) -> None:  # noqa
        self._underlying = underlying

    @property
    def underlying(self) -> logging.Filterer:
        return self._underlying

    @property
    def filters(self):
        return self._underlying.filters

    @filters.setter
    def filters(self, filters):
        self._underlying.filters = filters

    def addFilter(self, filter):  # noqa
        self._underlying.addFilter(filter)

    def removeFilter(self, filter):  # noqa
        self._underlying.removeFilter(filter)

    def filter(self, record):
        return self._underlying.filter(record)


class ProxyLogHandler(ProxyLogFilterer, logging.Handler):
    def __init__(self, underlying: logging.Handler) -> None:  # noqa
        ProxyLogFilterer.__init__(self, underlying)

    _underlying: logging.Handler

    @property
    def underlying(self) -> logging.Handler:
        return self._underlying

    def get_name(self):
        return self._underlying.get_name()

    def set_name(self, name):
        self._underlying.set_name(name)

    @property
    def name(self):
        return self._underlying.name

    @property
    def level(self):
        return self._underlying.level

    @level.setter
    def level(self, level):
        self._underlying.level = level

    @property
    def formatter(self):
        return self._underlying.formatter

    @formatter.setter
    def formatter(self, formatter):
        self._underlying.formatter = formatter

    def createLock(self):
        self._underlying.createLock()

    def acquire(self):
        self._underlying.acquire()

    def release(self):
        self._underlying.release()

    def setLevel(self, level):
        self._underlying.setLevel(level)

    def format(self, record):
        return self._underlying.format(record)

    def emit(self, record):
        self._underlying.emit(record)

    def handle(self, record):
        return self._underlying.handle(record)

    def setFormatter(self, fmt):
        self._underlying.setFormatter(fmt)

    def flush(self):
        self._underlying.flush()

    def close(self):
        self._underlying.close()

    def handleError(self, record):
        self._underlying.handleError(record)


##


class StandardLogHandler(ProxyLogHandler):
    pass


##


@contextlib.contextmanager
def _locking_logging_module_lock() -> ta.Iterator[None]:
    if hasattr(logging, '_acquireLock'):
        logging._acquireLock()  # noqa
        try:
            yield
        finally:
            logging._releaseLock()  # type: ignore  # noqa

    elif hasattr(logging, '_lock'):
        # https://github.com/python/cpython/commit/74723e11109a320e628898817ab449b3dad9ee96
        with logging._lock:  # noqa
            yield

    else:
        raise Exception("Can't find lock in logging module")


def configure_standard_logging(
        level: ta.Union[int, str] = logging.INFO,
        *,
        json: bool = False,
        target: ta.Optional[logging.Logger] = None,
        force: bool = False,
) -> ta.Optional[StandardLogHandler]:
    with _locking_logging_module_lock():
        if target is None:
            target = logging.root

        #

        if not force:
            if any(isinstance(h, StandardLogHandler) for h in list(target.handlers)):
                return None

        #

        handler = logging.StreamHandler()

        #

        formatter: logging.Formatter
        if json:
            formatter = JsonLogFormatter()
        else:
            formatter = StandardLogFormatter(StandardLogFormatter.build_log_format(STANDARD_LOG_FORMAT_PARTS))
        handler.setFormatter(formatter)

        #

        handler.addFilter(TidLogFilter())

        #

        target.addHandler(handler)

        #

        if level is not None:
            target.setLevel(level)

        #

        return StandardLogHandler(handler)


########################################
# ../events.py


class EventCallbacks:
    def __init__(self) -> None:
        super().__init__()

        self._callbacks: ta.List[ta.Tuple[type, ta.Callable]] = []

    def subscribe(self, type, callback):  # noqa
        self._callbacks.append((type, callback))

    def unsubscribe(self, type, callback):  # noqa
        self._callbacks.remove((type, callback))

    def notify(self, event):
        for type, callback in self._callbacks:  # noqa
            if isinstance(event, type):
                callback(event)

    def clear(self):
        self._callbacks[:] = []


EVENT_CALLBACKS = EventCallbacks()

notify_event = EVENT_CALLBACKS.notify
clear_events = EVENT_CALLBACKS.clear


class Event:
    """Abstract event type """


class ProcessLogEvent(Event):
    """Abstract"""
    channel: ta.Optional[str] = None

    def __init__(self, process, pid, data):
        super().__init__()
        self.process = process
        self.pid = pid
        self.data = data

    def payload(self):
        groupname = ''
        if self.process.group is not None:
            groupname = self.process.group.config.name
        try:
            data = as_string(self.data)
        except UnicodeDecodeError:
            data = f'Undecodable: {self.data!r}'
        fmt = as_string('processname:%s groupname:%s pid:%s channel:%s\n%s')
        result = fmt % (
            as_string(self.process.config.name),
            as_string(groupname),
            self.pid,
            as_string(self.channel),  # type: ignore
            data,
        )
        return result


class ProcessLogStdoutEvent(ProcessLogEvent):
    channel = 'stdout'


class ProcessLogStderrEvent(ProcessLogEvent):
    channel = 'stderr'


class ProcessCommunicationEvent(Event):
    """ Abstract """
    # event mode tokens
    BEGIN_TOKEN = b'<!--XSUPERVISOR:BEGIN-->'
    END_TOKEN = b'<!--XSUPERVISOR:END-->'

    def __init__(self, process, pid, data):
        super().__init__()
        self.process = process
        self.pid = pid
        self.data = data

    def payload(self):
        groupname = ''
        if self.process.group is not None:
            groupname = self.process.group.config.name
        try:
            data = as_string(self.data)
        except UnicodeDecodeError:
            data = f'Undecodable: {self.data!r}'
        return f'processname:{self.process.config.name} groupname:{groupname} pid:{self.pid}\n{data}'


class ProcessCommunicationStdoutEvent(ProcessCommunicationEvent):
    channel = 'stdout'


class ProcessCommunicationStderrEvent(ProcessCommunicationEvent):
    channel = 'stderr'


class RemoteCommunicationEvent(Event):
    def __init__(self, type, data):  # noqa
        super().__init__()
        self.type = type
        self.data = data

    def payload(self):
        return f'type:{self.type}\n{self.data}'


class SupervisorStateChangeEvent(Event):
    """ Abstract class """

    def payload(self):
        return ''


class SupervisorRunningEvent(SupervisorStateChangeEvent):
    pass


class SupervisorStoppingEvent(SupervisorStateChangeEvent):
    pass


class EventRejectedEvent:  # purposely does not subclass Event
    def __init__(self, process, event):
        super().__init__()
        self.process = process
        self.event = event


class ProcessStateEvent(Event):
    """ Abstract class, never raised directly """
    frm = None
    to = None

    def __init__(self, process, from_state, expected=True):
        super().__init__()
        self.process = process
        self.from_state = from_state
        self.expected = expected
        # we eagerly render these so if the process pid, etc changes beneath
        # us, we stash the values at the time the event was sent
        self.extra_values = self.get_extra_values()

    def payload(self):
        groupname = ''
        if self.process.group is not None:
            groupname = self.process.group.config.name
        l = [
            ('processname', self.process.config.name),
            ('groupname', groupname),
            ('from_state', get_process_state_description(self.from_state)),
        ]
        l.extend(self.extra_values)
        s = ' '.join([f'{name}:{val}' for name, val in l])
        return s

    def get_extra_values(self):
        return []


class ProcessStateFatalEvent(ProcessStateEvent):
    pass


class ProcessStateUnknownEvent(ProcessStateEvent):
    pass


class ProcessStateStartingOrBackoffEvent(ProcessStateEvent):
    def get_extra_values(self):
        return [('tries', int(self.process.backoff))]


class ProcessStateBackoffEvent(ProcessStateStartingOrBackoffEvent):
    pass


class ProcessStateStartingEvent(ProcessStateStartingOrBackoffEvent):
    pass


class ProcessStateExitedEvent(ProcessStateEvent):
    def get_extra_values(self):
        return [('expected', int(self.expected)), ('pid', self.process.pid)]


class ProcessStateRunningEvent(ProcessStateEvent):
    def get_extra_values(self):
        return [('pid', self.process.pid)]


class ProcessStateStoppingEvent(ProcessStateEvent):
    def get_extra_values(self):
        return [('pid', self.process.pid)]


class ProcessStateStoppedEvent(ProcessStateEvent):
    def get_extra_values(self):
        return [('pid', self.process.pid)]


class ProcessGroupEvent(Event):
    def __init__(self, group):
        super().__init__()
        self.group = group

    def payload(self):
        return f'groupname:{self.group}\n'


class ProcessGroupAddedEvent(ProcessGroupEvent):
    pass


class ProcessGroupRemovedEvent(ProcessGroupEvent):
    pass


class TickEvent(Event):
    """ Abstract """

    def __init__(self, when, supervisord):
        super().__init__()
        self.when = when
        self.supervisord = supervisord

    def payload(self):
        return f'when:{self.when}'


class Tick5Event(TickEvent):
    period = 5


class Tick60Event(TickEvent):
    period = 60


class Tick3600Event(TickEvent):
    period = 3600


TICK_EVENTS = [  # imported elsewhere
    Tick5Event,
    Tick60Event,
    Tick3600Event,
]


class EventTypes:
    EVENT = Event  # abstract

    PROCESS_STATE = ProcessStateEvent  # abstract
    PROCESS_STATE_STOPPED = ProcessStateStoppedEvent
    PROCESS_STATE_EXITED = ProcessStateExitedEvent
    PROCESS_STATE_STARTING = ProcessStateStartingEvent
    PROCESS_STATE_STOPPING = ProcessStateStoppingEvent
    PROCESS_STATE_BACKOFF = ProcessStateBackoffEvent
    PROCESS_STATE_FATAL = ProcessStateFatalEvent
    PROCESS_STATE_RUNNING = ProcessStateRunningEvent
    PROCESS_STATE_UNKNOWN = ProcessStateUnknownEvent

    PROCESS_COMMUNICATION = ProcessCommunicationEvent  # abstract
    PROCESS_COMMUNICATION_STDOUT = ProcessCommunicationStdoutEvent
    PROCESS_COMMUNICATION_STDERR = ProcessCommunicationStderrEvent

    PROCESS_LOG = ProcessLogEvent
    PROCESS_LOG_STDOUT = ProcessLogStdoutEvent
    PROCESS_LOG_STDERR = ProcessLogStderrEvent

    REMOTE_COMMUNICATION = RemoteCommunicationEvent

    SUPERVISOR_STATE_CHANGE = SupervisorStateChangeEvent  # abstract
    SUPERVISOR_STATE_CHANGE_RUNNING = SupervisorRunningEvent
    SUPERVISOR_STATE_CHANGE_STOPPING = SupervisorStoppingEvent

    TICK = TickEvent  # abstract
    TICK_5 = Tick5Event
    TICK_60 = Tick60Event
    TICK_3600 = Tick3600Event

    PROCESS_GROUP = ProcessGroupEvent  # abstract
    PROCESS_GROUP_ADDED = ProcessGroupAddedEvent
    PROCESS_GROUP_REMOVED = ProcessGroupRemovedEvent


def get_event_name_by_type(requested):
    for name, typ in EventTypes.__dict__.items():
        if typ is requested:
            return name
    return None


def register(name, event):
    setattr(EventTypes, name, event)


########################################
# ../types.py


class AbstractServerContext(abc.ABC):
    @property
    @abc.abstractmethod
    def config(self) -> ServerConfig:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def state(self) -> SupervisorState:
        raise NotImplementedError

    @abc.abstractmethod
    def set_state(self, state: SupervisorState) -> None:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def pid_history(self) -> ta.Dict[int, 'AbstractSubprocess']:
        raise NotImplementedError


class AbstractSubprocess(abc.ABC):
    @property
    @abc.abstractmethod
    def pid(self) -> int:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def config(self) -> ProcessConfig:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def context(self) -> AbstractServerContext:
        raise NotImplementedError

    @abc.abstractmethod
    def finish(self, sts: int) -> None:
        raise NotImplementedError


########################################
# ../context.py


log = logging.getLogger(__name__)


class ServerContext(AbstractServerContext):
    first = False
    test = False

    ##

    def __init__(self, config: ServerConfig) -> None:
        super().__init__()

        self._config = config

        self._pid_history: ta.Dict[int, AbstractSubprocess] = {}
        self._state: SupervisorState = SupervisorStates.RUNNING

        self.signal_receiver = SignalReceiver()

        self.poller = Poller()

        if self.config.user is not None:
            uid = name_to_uid(self.config.user)
            self.uid = uid
            self.gid = gid_for_uid(uid)
        else:
            self.uid = None
            self.gid = None

        self.unlink_pidfile = False

    @property
    def config(self) -> ServerConfig:
        return self._config

    @property
    def state(self) -> SupervisorState:
        return self._state

    def set_state(self, state: SupervisorState) -> None:
        self._state = state

    @property
    def pid_history(self) -> ta.Dict[int, AbstractSubprocess]:
        return self._pid_history

    uid: ta.Optional[int]
    gid: ta.Optional[int]

    ##

    def set_signals(self) -> None:
        self.signal_receiver.install(
            signal.SIGTERM,
            signal.SIGINT,
            signal.SIGQUIT,
            signal.SIGHUP,
            signal.SIGCHLD,
            signal.SIGUSR2,
        )

    def waitpid(self) -> ta.Tuple[ta.Optional[int], ta.Optional[int]]:
        # Need pthread_sigmask here to avoid concurrent sigchld, but Python doesn't offer in Python < 3.4.  There is
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
                log.critical('waitpid error %r; a process may not be cleaned up properly', code)
            if code == errno.EINTR:
                log.debug('EINTR during reap')
            pid, sts = None, None
        return pid, sts

    def set_uid_or_exit(self) -> None:
        """
        Set the uid of the supervisord process.  Called during supervisord startup only.  No return value.  Exits the
        process via usage() if privileges could not be dropped.
        """
        if self.uid is None:
            if os.getuid() == 0:
                warnings.warn(
                    'Supervisor is running as root.  Privileges were not dropped because no user is specified in the '
                    'config file.  If you intend to run as root, you can set user=root in the config file to avoid '
                    'this message.',
                )
        else:
            msg = drop_privileges(self.uid)
            if msg is None:
                log.info('Set uid to user %s succeeded', self.uid)
            else:  # failed to drop privileges
                raise RuntimeError(msg)

    def set_rlimits_or_exit(self) -> None:
        """
        Set the rlimits of the supervisord process.  Called during supervisord startup only.  No return value.  Exits
        the process via usage() if any rlimits could not be set.
        """

        limits = []

        if hasattr(resource, 'RLIMIT_NOFILE'):
            limits.append({
                'msg': (
                    'The minimum number of file descriptors required to run this process is %(min_limit)s as per the '
                    '"minfds" command-line argument or config file setting. The current environment will only allow '
                    'you to open %(hard)s file descriptors.  Either raise the number of usable file descriptors in '
                    'your environment (see README.rst) or lower the minfds setting in the config file to allow the '
                    'process to start.'
                ),
                'min': self.config.minfds,
                'resource': resource.RLIMIT_NOFILE,
                'name': 'RLIMIT_NOFILE',
            })

        if hasattr(resource, 'RLIMIT_NPROC'):
            limits.append({
                'msg': (
                    'The minimum number of available processes required to run this program is %(min_limit)s as per '
                    'the "minprocs" command-line argument or config file setting. The current environment will only '
                    'allow you to open %(hard)s processes.  Either raise the number of usable processes in your '
                    'environment (see README.rst) or lower the minprocs setting in the config file to allow the '
                    'program to start.'
                ),
                'min': self.config.minprocs,
                'resource': resource.RLIMIT_NPROC,
                'name': 'RLIMIT_NPROC',
            })

        for limit in limits:
            min_limit = limit['min']
            res = limit['resource']
            msg = limit['msg']
            name = limit['name']

            soft, hard = resource.getrlimit(res)  # type: ignore

            # -1 means unlimited
            if soft < min_limit and soft != -1:  # type: ignore
                if hard < min_limit and hard != -1:  # type: ignore
                    # setrlimit should increase the hard limit if we are root, if not then setrlimit raises and we print
                    # usage
                    hard = min_limit  # type: ignore

                try:
                    resource.setrlimit(res, (min_limit, hard))  # type: ignore
                    log.info('Increased %s limit to %s', name, min_limit)
                except (resource.error, ValueError):
                    raise RuntimeError(msg % dict(  # type: ignore  # noqa
                        min_limit=min_limit,
                        res=res,
                        name=name,
                        soft=soft,
                        hard=hard,
                    ))

    def cleanup(self) -> None:
        if self.unlink_pidfile:
            try_unlink(self.config.pidfile)
        self.poller.close()

    def cleanup_fds(self) -> None:
        # try to close any leaked file descriptors (for reload)
        start = 5
        os.closerange(start, self.config.minfds)

    def clear_auto_child_logdir(self) -> None:
        # must be called after realize()
        child_logdir = self.config.child_logdir
        fnre = re.compile(rf'.+?---{self.config.identifier}-\S+\.log\.?\d{{0,4}}')
        try:
            filenames = os.listdir(child_logdir)
        except OSError:
            log.warning('Could not clear child_log dir')
            return

        for filename in filenames:
            if fnre.match(filename):
                pathname = os.path.join(child_logdir, filename)
                try:
                    os.remove(pathname)
                except OSError:
                    log.warning('Failed to clean up %r', pathname)

    def daemonize(self) -> None:
        self.poller.before_daemonize()
        self._daemonize()
        self.poller.after_daemonize()

    def _daemonize(self) -> None:
        # To daemonize, we need to become the leader of our own session (process) group.  If we do not, signals sent to
        # our parent process will also be sent to us.   This might be bad because signals such as SIGINT can be sent to
        # our parent process during normal (uninteresting) operations such as when we press Ctrl-C in the parent
        # terminal window to escape from a logtail command. To disassociate ourselves from our parent's session group we
        # use os.setsid.  It means "set session id", which has the effect of disassociating a process from is current
        # session and process group and setting itself up as a new session leader.
        #
        # Unfortunately we cannot call setsid if we're already a session group leader, so we use "fork" to make a copy
        # of ourselves that is guaranteed to not be a session group leader.
        #
        # We also change directories, set stderr and stdout to null, and change our umask.
        #
        # This explanation was (gratefully) garnered from
        # http://www.cems.uwe.ac.uk/~irjohnso/coursenotes/lrc/system/daemons/d3.htm

        pid = os.fork()
        if pid != 0:
            # Parent
            log.debug('supervisord forked; parent exiting')
            real_exit(0)
        # Child
        log.info('daemonizing the supervisord process')
        if self.config.directory:
            try:
                os.chdir(self.config.directory)
            except OSError as err:
                log.critical("can't chdir into %r: %s", self.config.directory, err)
            else:
                log.info('set current directory: %r', self.config.directory)
        os.dup2(0, os.open('/dev/null', os.O_RDONLY))
        os.dup2(1, os.open('/dev/null', os.O_WRONLY))
        os.dup2(2, os.open('/dev/null', os.O_WRONLY))
        os.setsid()
        os.umask(self.config.umask)
        # XXX Stevens, in his Advanced Unix book, section 13.3 (page 417) recommends calling umask(0) and closing unused
        # file descriptors.  In his Network Programming book, he additionally recommends ignoring SIGHUP and forking
        # again after the setsid() call, for obscure SVR4 reasons.

    def get_auto_child_log_name(self, name: str, identifier: str, channel: str) -> str:
        prefix = f'{name}-{channel}---{identifier}-'
        logfile = mktempfile(
            suffix='.log',
            prefix=prefix,
            dir=self.config.child_logdir,
        )
        return logfile

    def get_signal(self) -> ta.Optional[int]:
        return self.signal_receiver.get_signal()

    def write_pidfile(self) -> None:
        pid = os.getpid()
        try:
            with open(self.config.pidfile, 'w') as f:
                f.write(f'{pid}\n')
        except OSError:
            log.critical('could not write pidfile %s', self.config.pidfile)
        else:
            self.unlink_pidfile = True
            log.info('supervisord started with pid %s', pid)


def drop_privileges(user: ta.Union[int, str, None]) -> ta.Optional[str]:
    """
    Drop privileges to become the specified user, which may be a username or uid.  Called for supervisord startup
    and when spawning subprocesses.  Returns None on success or a string error message if privileges could not be
    dropped.
    """
    if user is None:
        return 'No user specified to setuid to!'

    # get uid for user, which can be a number or username
    try:
        uid = int(user)
    except ValueError:
        try:
            pwrec = pwd.getpwnam(user)  # type: ignore
        except KeyError:
            return f"Can't find username {user!r}"
        uid = pwrec[2]
    else:
        try:
            pwrec = pwd.getpwuid(uid)
        except KeyError:
            return f"Can't find uid {uid!r}"

    current_uid = os.getuid()

    if current_uid == uid:
        # do nothing and return successfully if the uid is already the current one.  this allows a supervisord
        # running as an unprivileged user "foo" to start a process where the config has "user=foo" (same user) in
        # it.
        return None

    if current_uid != 0:
        return "Can't drop privilege as nonroot user"

    gid = pwrec[3]
    if hasattr(os, 'setgroups'):
        user = pwrec[0]
        groups = [grprec[2] for grprec in grp.getgrall() if user in grprec[3]]

        # always put our primary gid first in this list, otherwise we can lose group info since sometimes the first
        # group in the setgroups list gets overwritten on the subsequent setgid call (at least on freebsd 9 with
        # python 2.7 - this will be safe though for all unix /python version combos)
        groups.insert(0, gid)
        try:
            os.setgroups(groups)
        except OSError:
            return 'Could not set groups of effective user'
    try:
        os.setgid(gid)
    except OSError:
        return 'Could not set group id of effective user'
    os.setuid(uid)
    return None


def make_pipes(stderr=True) -> ta.Mapping[str, int]:
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
        stdin, child_stdin = os.pipe()
        pipes['child_stdin'], pipes['stdin'] = stdin, child_stdin
        stdout, child_stdout = os.pipe()
        pipes['stdout'], pipes['child_stdout'] = stdout, child_stdout
        if stderr:
            stderr, child_stderr = os.pipe()
            pipes['stderr'], pipes['child_stderr'] = stderr, child_stderr
        for fd in (pipes['stdout'], pipes['stderr'], pipes['stdin']):
            if fd is not None:
                flags = fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NDELAY
                fcntl.fcntl(fd, fcntl.F_SETFL, flags)
        return pipes  # type: ignore
    except OSError:
        for fd in pipes.values():
            if fd is not None:
                close_fd(fd)
        raise


def close_parent_pipes(pipes: ta.Mapping[str, int]) -> None:
    for fdname in ('stdin', 'stdout', 'stderr'):
        fd = pipes.get(fdname)
        if fd is not None:
            close_fd(fd)


def close_child_pipes(pipes: ta.Mapping[str, int]) -> None:
    for fdname in ('child_stdin', 'child_stdout', 'child_stderr'):
        fd = pipes.get(fdname)
        if fd is not None:
            close_fd(fd)


def check_execv_args(filename, argv, st) -> None:
    if st is None:
        raise NotFoundError(f"can't find command {filename!r}")

    elif stat.S_ISDIR(st[stat.ST_MODE]):
        raise NotExecutableError(f'command at {filename!r} is a directory')

    elif not (stat.S_IMODE(st[stat.ST_MODE]) & 0o111):
        raise NotExecutableError(f'command at {filename!r} is not executable')

    elif not os.access(filename, os.X_OK):
        raise NoPermissionError(f'no permission to run command {filename!r}')


########################################
# ../dispatchers.py


log = logging.getLogger(__name__)


class Dispatcher(abc.ABC):

    def __init__(self, process: AbstractSubprocess, channel: str, fd: int) -> None:
        super().__init__()

        self._process = process  # process which "owns" this dispatcher
        self._channel = channel  # 'stderr' or 'stdout'
        self._fd = fd
        self._closed = False  # True if close() has been called

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} at {id(self)} for {self._process} ({self._channel})>'

    @property
    def process(self) -> AbstractSubprocess:
        return self._process

    @property
    def channel(self) -> str:
        return self._channel

    @property
    def fd(self) -> int:
        return self._fd

    @property
    def closed(self) -> bool:
        return self._closed

    @abc.abstractmethod
    def readable(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def writable(self) -> bool:
        raise NotImplementedError

    def handle_read_event(self) -> None:
        raise TypeError

    def handle_write_event(self) -> None:
        raise TypeError

    def handle_error(self) -> None:
        nil, t, v, tbinfo = compact_traceback()

        log.critical('uncaptured python exception, closing channel %s (%s:%s %s)', repr(self), t, v, tbinfo)
        self.close()

    def close(self) -> None:
        if not self._closed:
            log.debug('fd %s closed, stopped monitoring %s', self._fd, self)
            self._closed = True

    def flush(self) -> None:  # noqa
        pass


class OutputDispatcher(Dispatcher):
    """
    Dispatcher for one channel (stdout or stderr) of one process. Serves several purposes:

    - capture output sent within <!--XSUPERVISOR:BEGIN--> and <!--XSUPERVISOR:END--> tags and signal a
      ProcessCommunicationEvent by calling notify_event(event).
    - route the output to the appropriate log handlers as specified in the config.
    """

    def __init__(self, process: AbstractSubprocess, event_type, fd):
        """
        Initialize the dispatcher.

        `event_type` should be one of ProcessLogStdoutEvent or ProcessLogStderrEvent
        """
        super().__init__(process, event_type.channel, fd)
        self.event_type = event_type

        self.lc: ProcessConfig.Log = getattr(process.config, self._channel)

        self._init_normal_log()
        self._init_capture_log()

        self._child_log = self._normal_log

        self._capture_mode = False  # are we capturing process event data
        self._output_buffer = b''  # data waiting to be logged

        # all code below is purely for minor speedups
        begin_token = self.event_type.BEGIN_TOKEN
        end_token = self.event_type.END_TOKEN
        self.begin_token_data = (begin_token, len(begin_token))
        self.end_token_data = (end_token, len(end_token))
        self.main_log_level = logging.DEBUG
        config = self._process.config
        self.log_to_main_log = process.context.config.loglevel <= self.main_log_level
        self.stdout_events_enabled = config.stdout.events_enabled
        self.stderr_events_enabled = config.stderr.events_enabled

    _child_log: ta.Optional[logging.Logger]  # the current logger (normal_log or capture_log)
    _normal_log: ta.Optional[logging.Logger]  # the "normal" (non-capture) logger
    _capture_log: ta.Optional[logging.Logger]  # the logger used while we're in capture_mode

    def _init_normal_log(self) -> None:
        """
        Configure the "normal" (non-capture) log for this channel of this process. Sets self.normal_log if logging is
        enabled.
        """
        config = self._process.config  # noqa
        channel = self._channel  # noqa

        logfile = self.lc.file
        maxbytes = self.lc.maxbytes  # noqa
        backups = self.lc.backups  # noqa
        to_syslog = self.lc.syslog

        if logfile or to_syslog:
            self._normal_log = logging.getLogger(__name__)

        # if logfile:
        #     loggers.handle_file(
        #         self.normal_log,
        #         filename=logfile,
        #         fmt='%(message)s',
        #         rotating=bool(maxbytes),  # optimization
        #         maxbytes=maxbytes,
        #         backups=backups,
        #     )
        #
        # if to_syslog:
        #     loggers.handle_syslog(
        #         self.normal_log,
        #         fmt=config.name + ' %(message)s',
        #     )

    def _init_capture_log(self) -> None:
        """
        Configure the capture log for this process.  This log is used to temporarily capture output when special output
        is detected. Sets self.capture_log if capturing is enabled.
        """
        capture_maxbytes = self.lc.capture_maxbytes
        if capture_maxbytes:
            self._capture_log = logging.getLogger(__name__)
            # loggers.handle_boundIO(
            #     self._capture_log,
            #     fmt='%(message)s',
            #     maxbytes=capture_maxbytes,
            # )

    def remove_logs(self):
        for log in (self._normal_log, self._capture_log):
            if log is not None:
                for handler in log.handlers:
                    handler.remove()  # type: ignore
                    handler.reopen()  # type: ignore

    def reopen_logs(self):
        for log in (self._normal_log, self._capture_log):
            if log is not None:
                for handler in log.handlers:
                    handler.reopen()  # type: ignore

    def _log(self, data):
        if data:
            if self._process.context.config.strip_ansi:
                data = strip_escapes(data)
            if self._child_log:
                self._child_log.info(data)
            if self.log_to_main_log:
                if not isinstance(data, bytes):
                    text = data
                else:
                    try:
                        text = data.decode('utf-8')
                    except UnicodeDecodeError:
                        text = f'Undecodable: {data!r}'
                log.log(self.main_log_level, '%r %s output:\n%s', self._process.config.name, self._channel, text)  # noqa
            if self._channel == 'stdout':
                if self.stdout_events_enabled:
                    notify_event(ProcessLogStdoutEvent(self._process, self._process.pid, data))
            elif self.stderr_events_enabled:
                notify_event(ProcessLogStderrEvent(self._process, self._process.pid, data))

    def record_output(self):
        if self._capture_log is None:
            # shortcut trying to find capture data
            data = self._output_buffer
            self._output_buffer = b''
            self._log(data)
            return

        if self._capture_mode:
            token, tokenlen = self.end_token_data
        else:
            token, tokenlen = self.begin_token_data

        if len(self._output_buffer) <= tokenlen:
            return  # not enough data

        data = self._output_buffer
        self._output_buffer = b''

        try:
            before, after = data.split(token, 1)
        except ValueError:
            after = None
            index = find_prefix_at_end(data, token)
            if index:
                self._output_buffer = self._output_buffer + data[-index:]
                data = data[:-index]
            self._log(data)
        else:
            self._log(before)
            self.toggle_capture_mode()
            self._output_buffer = after  # type: ignore

        if after:
            self.record_output()

    def toggle_capture_mode(self):
        self._capture_mode = not self._capture_mode

        if self._capture_log is not None:
            if self._capture_mode:
                self._child_log = self._capture_log
            else:
                for handler in self._capture_log.handlers:
                    handler.flush()
                data = self._capture_log.getvalue()  # type: ignore
                channel = self._channel
                procname = self._process.config.name
                event = self.event_type(self._process, self._process.pid, data)
                notify_event(event)

                log.debug('%r %s emitted a comm event', procname, channel)
                for handler in self._capture_log.handlers:
                    handler.remove()  # type: ignore
                    handler.reopen()  # type: ignore
                self._child_log = self._normal_log

    def writable(self) -> bool:
        return False

    def readable(self) -> bool:
        if self._closed:
            return False
        return True

    def handle_read_event(self) -> None:
        data = readfd(self._fd)
        self._output_buffer += data
        self.record_output()
        if not data:
            # if we get no data back from the pipe, it means that the child process has ended.  See
            # mail.python.org/pipermail/python-dev/2004-August/046850.html
            self.close()


class InputDispatcher(Dispatcher):

    def __init__(self, process: AbstractSubprocess, channel: str, fd: int) -> None:
        super().__init__(process, channel, fd)
        self._input_buffer = b''

    def writable(self) -> bool:
        if self._input_buffer and not self._closed:
            return True
        return False

    def readable(self) -> bool:
        return False

    def flush(self) -> None:
        # other code depends on this raising EPIPE if the pipe is closed
        sent = os.write(self._fd, as_bytes(self._input_buffer))
        self._input_buffer = self._input_buffer[sent:]

    def handle_write_event(self) -> None:
        if self._input_buffer:
            try:
                self.flush()
            except OSError as why:
                if why.args[0] == errno.EPIPE:
                    self._input_buffer = b''
                    self.close()
                else:
                    raise


########################################
# ../process.py


log = logging.getLogger(__name__)


@functools.total_ordering
class Subprocess(AbstractSubprocess):
    """A class to manage a subprocess."""

    # Initial state; overridden by instance variables

    # pid = 0  # Subprocess pid; 0 when not running
    # config = None  # ProcessConfig instance
    # state = None  # process state code
    listener_state = None  # listener state code (if we're an event listener)
    event = None  # event currently being processed (if we're an event listener)
    laststart = 0.  # Last time the subprocess was started; 0 if never
    laststop = 0.  # Last time the subprocess was stopped; 0 if never
    last_stop_report = 0.  # Last time "waiting for x to stop" logged, to throttle
    delay = 0.  # If nonzero, delay starting or killing until this time
    administrative_stop = False  # true if process has been stopped by an admin
    system_stop = False  # true if process has been stopped by the system
    killing = False  # true if we are trying to kill this process
    backoff = 0  # backoff counter (to startretries)
    dispatchers = None  # asyncore output dispatchers (keyed by fd)
    pipes = None  # map of channel name to file descriptor #
    exitstatus = None  # status attached to dead process by finish()
    spawn_err = None  # error message attached by spawn() if any
    group = None  # ProcessGroup instance if process is in the group

    def __init__(self, config: ProcessConfig, group: 'ProcessGroup', context: AbstractServerContext) -> None:
        super().__init__()
        self._config = config
        self.group = group
        self._context = context
        self._dispatchers: dict = {}
        self._pipes: dict = {}
        self.state = ProcessStates.STOPPED
        self._pid = 0

    @property
    def pid(self) -> int:
        return self._pid

    @property
    def config(self) -> ProcessConfig:
        return self._config

    @property
    def context(self) -> AbstractServerContext:
        return self._context

    def remove_logs(self) -> None:
        for dispatcher in self._dispatchers.values():
            if hasattr(dispatcher, 'remove_logs'):
                dispatcher.remove_logs()

    def reopen_logs(self) -> None:
        for dispatcher in self._dispatchers.values():
            if hasattr(dispatcher, 'reopen_logs'):
                dispatcher.reopen_logs()

    def drain(self) -> None:
        for dispatcher in self._dispatchers.values():
            # note that we *must* call readable() for every dispatcher, as it may have side effects for a given
            # dispatcher (eg. call handle_listener_state_change for event listener processes)
            if dispatcher.readable():
                dispatcher.handle_read_event()
            if dispatcher.writable():
                dispatcher.handle_write_event()

    def write(self, chars: ta.Union[bytes, str]) -> None:
        if not self.pid or self.killing:
            raise OSError(errno.EPIPE, 'Process already closed')

        stdin_fd = self._pipes['stdin']
        if stdin_fd is None:
            raise OSError(errno.EPIPE, 'Process has no stdin channel')

        dispatcher = self._dispatchers[stdin_fd]
        if dispatcher.closed:
            raise OSError(errno.EPIPE, "Process' stdin channel is closed")

        dispatcher.input_buffer += chars
        dispatcher.flush()  # this must raise EPIPE if the pipe is closed

    def _get_execv_args(self) -> ta.Tuple[str, ta.Sequence[str]]:
        """
        Internal: turn a program name into a file name, using $PATH, make sure it exists / is executable, raising a
        ProcessError if not
        """
        try:
            commandargs = shlex.split(self.config.command)
        except ValueError as e:
            raise BadCommandError(f"can't parse command {self.config.command!r}: {e}")  # noqa

        if commandargs:
            program = commandargs[0]
        else:
            raise BadCommandError('command is empty')

        if '/' in program:
            filename = program
            try:
                st = os.stat(filename)
            except OSError:
                st = None

        else:
            path = get_path()
            found = None
            st = None
            for dir in path:  # noqa
                found = os.path.join(dir, program)
                try:
                    st = os.stat(found)
                except OSError:
                    pass
                else:
                    break
            if st is None:
                filename = program
            else:
                filename = found  # type: ignore

        # check_execv_args will raise a ProcessError if the execv args are bogus, we break it out into a separate
        # options method call here only to service unit tests
        check_execv_args(filename, commandargs, st)

        return filename, commandargs

    event_map: ta.ClassVar[ta.Mapping[int, ta.Type[ProcessStateEvent]]] = {
        ProcessStates.BACKOFF: ProcessStateBackoffEvent,
        ProcessStates.FATAL: ProcessStateFatalEvent,
        ProcessStates.UNKNOWN: ProcessStateUnknownEvent,
        ProcessStates.STOPPED: ProcessStateStoppedEvent,
        ProcessStates.EXITED: ProcessStateExitedEvent,
        ProcessStates.RUNNING: ProcessStateRunningEvent,
        ProcessStates.STARTING: ProcessStateStartingEvent,
        ProcessStates.STOPPING: ProcessStateStoppingEvent,
    }

    def change_state(self, new_state: ProcessState, expected: bool = True) -> bool:
        old_state = self.state
        if new_state is old_state:
            return False

        self.state = new_state
        if new_state == ProcessStates.BACKOFF:
            now = time.time()
            self.backoff += 1
            self.delay = now + self.backoff

        event_class = self.event_map.get(new_state)
        if event_class is not None:
            event = event_class(self, old_state, expected)
            notify_event(event)

        return True

    def _check_in_state(self, *states: ProcessState) -> None:
        if self.state not in states:
            current_state = get_process_state_description(self.state)
            allowable_states = ' '.join(map(get_process_state_description, states))
            processname = as_string(self.config.name)
            raise AssertionError('Assertion failed for %s: %s not in %s' % (processname, current_state, allowable_states))  # noqa

    def _record_spawn_err(self, msg: str) -> None:
        self.spawn_err = msg
        log.info('spawn_err: %s', msg)

    def spawn(self) -> ta.Optional[int]:
        processname = as_string(self.config.name)

        if self.pid:
            log.warning('process \'%s\' already running', processname)
            return None

        self.killing = False
        self.spawn_err = None
        self.exitstatus = None
        self.system_stop = False
        self.administrative_stop = False

        self.laststart = time.time()

        self._check_in_state(
            ProcessStates.EXITED,
            ProcessStates.FATAL,
            ProcessStates.BACKOFF,
            ProcessStates.STOPPED,
        )

        self.change_state(ProcessStates.STARTING)

        try:
            filename, argv = self._get_execv_args()
        except ProcessError as what:
            self._record_spawn_err(what.args[0])
            self._check_in_state(ProcessStates.STARTING)
            self.change_state(ProcessStates.BACKOFF)
            return None

        try:
            self._dispatchers, self._pipes = self._make_dispatchers()  # type: ignore
        except OSError as why:
            code = why.args[0]
            if code == errno.EMFILE:
                # too many file descriptors open
                msg = f"too many open files to spawn '{processname}'"
            else:
                msg = f"unknown error making dispatchers for '{processname}': {errno.errorcode.get(code, code)}"
            self._record_spawn_err(msg)
            self._check_in_state(ProcessStates.STARTING)
            self.change_state(ProcessStates.BACKOFF)
            return None

        try:
            pid = os.fork()
        except OSError as why:
            code = why.args[0]
            if code == errno.EAGAIN:
                # process table full
                msg = f'Too many processes in process table to spawn \'{processname}\''
            else:
                msg = f'unknown error during fork for \'{processname}\': {errno.errorcode.get(code, code)}'
            self._record_spawn_err(msg)
            self._check_in_state(ProcessStates.STARTING)
            self.change_state(ProcessStates.BACKOFF)
            close_parent_pipes(self._pipes)
            close_child_pipes(self._pipes)
            return None

        if pid != 0:
            return self._spawn_as_parent(pid)

        else:
            self._spawn_as_child(filename, argv)
            return None

    def _make_dispatchers(self) -> ta.Tuple[ta.Mapping[int, Dispatcher], ta.Mapping[str, int]]:
        use_stderr = not self.config.redirect_stderr
        p = make_pipes(use_stderr)
        stdout_fd, stderr_fd, stdin_fd = p['stdout'], p['stderr'], p['stdin']
        dispatchers: ta.Dict[int, Dispatcher] = {}
        etype: ta.Type[ProcessCommunicationEvent]
        if stdout_fd is not None:
            etype = ProcessCommunicationStdoutEvent
            dispatchers[stdout_fd] = OutputDispatcher(self, etype, stdout_fd)
        if stderr_fd is not None:
            etype = ProcessCommunicationStderrEvent
            dispatchers[stderr_fd] = OutputDispatcher(self, etype, stderr_fd)
        if stdin_fd is not None:
            dispatchers[stdin_fd] = InputDispatcher(self, 'stdin', stdin_fd)
        return dispatchers, p

    def _spawn_as_parent(self, pid: int) -> int:
        # Parent
        self._pid = pid
        close_child_pipes(self._pipes)
        log.info('spawned: \'%s\' with pid %s', as_string(self.config.name), pid)
        self.spawn_err = None
        self.delay = time.time() + self.config.startsecs
        self.context.pid_history[pid] = self
        return pid

    def _prepare_child_fds(self) -> None:
        os.dup2(self._pipes['child_stdin'], 0)
        os.dup2(self._pipes['child_stdout'], 1)
        if self.config.redirect_stderr:
            os.dup2(self._pipes['child_stdout'], 2)
        else:
            os.dup2(self._pipes['child_stderr'], 2)
        for i in range(3, self.context.config.minfds):
            close_fd(i)

    def _spawn_as_child(self, filename: str, argv: ta.Sequence[str]) -> None:
        try:
            # prevent child from receiving signals sent to the parent by calling os.setpgrp to create a new process
            # group for the child; this prevents, for instance, the case of child processes being sent a SIGINT when
            # running supervisor in foreground mode and Ctrl-C in the terminal window running supervisord is pressed.
            # Presumably it also prevents HUP, etc received by supervisord from being sent to children.
            os.setpgrp()

            self._prepare_child_fds()
            # sending to fd 2 will put this output in the stderr log

            # set user
            setuid_msg = self.set_uid()
            if setuid_msg:
                uid = self.config.uid
                msg = f"couldn't setuid to {uid}: {setuid_msg}\n"
                os.write(2, as_bytes('supervisor: ' + msg))
                return  # finally clause will exit the child process

            # set environment
            env = os.environ.copy()
            env['SUPERVISOR_ENABLED'] = '1'
            env['SUPERVISOR_PROCESS_NAME'] = self.config.name
            if self.group:
                env['SUPERVISOR_GROUP_NAME'] = self.group.config.name
            if self.config.environment is not None:
                env.update(self.config.environment)

            # change directory
            cwd = self.config.directory
            try:
                if cwd is not None:
                    os.chdir(cwd)
            except OSError as why:
                code = errno.errorcode.get(why.args[0], why.args[0])
                msg = f"couldn't chdir to {cwd}: {code}\n"
                os.write(2, as_bytes('supervisor: ' + msg))
                return  # finally clause will exit the child process

            # set umask, then execve
            try:
                if self.config.umask is not None:
                    os.umask(self.config.umask)
                os.execve(filename, list(argv), env)
            except OSError as why:
                code = errno.errorcode.get(why.args[0], why.args[0])
                msg = f"couldn't exec {argv[0]}: {code}\n"
                os.write(2, as_bytes('supervisor: ' + msg))
            except Exception:  # noqa
                (file, fun, line), t, v, tbinfo = compact_traceback()
                error = f'{t}, {v}: file: {file} line: {line}'
                msg = f"couldn't exec {filename}: {error}\n"
                os.write(2, as_bytes('supervisor: ' + msg))

            # this point should only be reached if execve failed. the finally clause will exit the child process.

        finally:
            os.write(2, as_bytes('supervisor: child process was not spawned\n'))
            real_exit(127)  # exit process with code for spawn failure

    def _check_and_adjust_for_system_clock_rollback(self, test_time):
        """
        Check if system clock has rolled backward beyond test_time. If so, set affected timestamps to test_time.
        """
        if self.state == ProcessStates.STARTING:
            self.laststart = min(test_time, self.laststart)
            if self.delay > 0 and test_time < (self.delay - self.config.startsecs):
                self.delay = test_time + self.config.startsecs

        elif self.state == ProcessStates.RUNNING:
            if test_time > self.laststart and test_time < (self.laststart + self.config.startsecs):
                self.laststart = test_time - self.config.startsecs

        elif self.state == ProcessStates.STOPPING:
            self.last_stop_report = min(test_time, self.last_stop_report)
            if self.delay > 0 and test_time < (self.delay - self.config.stopwaitsecs):
                self.delay = test_time + self.config.stopwaitsecs

        elif self.state == ProcessStates.BACKOFF:
            if self.delay > 0 and test_time < (self.delay - self.backoff):
                self.delay = test_time + self.backoff

    def stop(self) -> ta.Optional[str]:
        self.administrative_stop = True
        self.last_stop_report = 0
        return self.kill(self.config.stopsignal)

    def stop_report(self) -> None:
        """ Log a 'waiting for x to stop' message with throttling. """
        if self.state == ProcessStates.STOPPING:
            now = time.time()

            self._check_and_adjust_for_system_clock_rollback(now)

            if now > (self.last_stop_report + 2):  # every 2 seconds
                log.info('waiting for %s to stop', as_string(self.config.name))
                self.last_stop_report = now

    def give_up(self) -> None:
        self.delay = 0
        self.backoff = 0
        self.system_stop = True
        self._check_in_state(ProcessStates.BACKOFF)
        self.change_state(ProcessStates.FATAL)

    def kill(self, sig: int) -> ta.Optional[str]:
        """
        Send a signal to the subprocess with the intention to kill it (to make it exit).  This may or may not actually
        kill it.

        Return None if the signal was sent, or an error message string if an error occurred or if the subprocess is not
        running.
        """
        now = time.time()

        processname = as_string(self.config.name)
        # If the process is in BACKOFF and we want to stop or kill it, then BACKOFF -> STOPPED.  This is needed because
        # if startretries is a large number and the process isn't starting successfully, the stop request would be
        # blocked for a long time waiting for the retries.
        if self.state == ProcessStates.BACKOFF:
            log.debug('Attempted to kill %s, which is in BACKOFF state.', processname)
            self.change_state(ProcessStates.STOPPED)
            return None

        args: tuple
        if not self.pid:
            fmt, args = "attempted to kill %s with sig %s but it wasn't running", (processname, signame(sig))
            log.debug(fmt, *args)
            return fmt % args

        # If we're in the stopping state, then we've already sent the stop signal and this is the kill signal
        if self.state == ProcessStates.STOPPING:
            killasgroup = self.config.killasgroup
        else:
            killasgroup = self.config.stopasgroup

        as_group = ''
        if killasgroup:
            as_group = 'process group '

        log.debug('killing %s (pid %s) %swith signal %s', processname, self.pid, as_group, signame(sig))

        # RUNNING/STARTING/STOPPING -> STOPPING
        self.killing = True
        self.delay = now + self.config.stopwaitsecs
        # we will already be in the STOPPING state if we're doing a SIGKILL as a result of overrunning stopwaitsecs
        self._check_in_state(ProcessStates.RUNNING, ProcessStates.STARTING, ProcessStates.STOPPING)
        self.change_state(ProcessStates.STOPPING)

        pid = self.pid
        if killasgroup:
            # send to the whole process group instead
            pid = -self.pid

        try:
            try:
                os.kill(pid, sig)
            except OSError as exc:
                if exc.errno == errno.ESRCH:
                    log.debug('unable to signal %s (pid %s), it probably just exited on its own: %s', processname, self.pid, str(exc))  # noqa
                    # we could change the state here but we intentionally do not.  we will do it during normal SIGCHLD
                    # processing.
                    return None
                raise
        except Exception:  # noqa
            tb = traceback.format_exc()
            fmt, args = 'unknown problem killing %s (%s):%s', (processname, self.pid, tb)
            log.critical(fmt, *args)
            self.change_state(ProcessStates.UNKNOWN)
            self.killing = False
            self.delay = 0
            return fmt % args

        return None

    def signal(self, sig: int) -> ta.Optional[str]:
        """
        Send a signal to the subprocess, without intending to kill it.

        Return None if the signal was sent, or an error message string if an error occurred or if the subprocess is not
        running.
        """
        processname = as_string(self.config.name)
        args: tuple
        if not self.pid:
            fmt, args = "attempted to send %s sig %s but it wasn't running", (processname, signame(sig))
            log.debug(fmt, *args)
            return fmt % args

        log.debug('sending %s (pid %s) sig %s', processname, self.pid, signame(sig))

        self._check_in_state(ProcessStates.RUNNING, ProcessStates.STARTING, ProcessStates.STOPPING)

        try:
            try:
                os.kill(self.pid, sig)
            except OSError as exc:
                if exc.errno == errno.ESRCH:
                    log.debug('unable to signal %s (pid %s), it probably just now exited '
                              'on its own: %s', processname, self.pid, str(exc))
                    # we could change the state here but we intentionally do not.  we will do it during normal SIGCHLD
                    # processing.
                    return None
                raise
        except Exception:  # noqa
            tb = traceback.format_exc()
            fmt, args = 'unknown problem sending sig %s (%s):%s', (processname, self.pid, tb)
            log.critical(fmt, *args)
            self.change_state(ProcessStates.UNKNOWN)
            return fmt % args

        return None

    def finish(self, sts: int) -> None:
        """ The process was reaped and we need to report and manage its state """
        self.drain()

        es, msg = decode_wait_status(sts)

        now = time.time()

        self._check_and_adjust_for_system_clock_rollback(now)

        self.laststop = now
        processname = as_string(self.config.name)

        if now > self.laststart:
            too_quickly = now - self.laststart < self.config.startsecs
        else:
            too_quickly = False
            log.warning(
                "process '%s' (%s) laststart time is in the future, don't "
                "know how long process was running so assuming it did "
                "not exit too quickly", processname, self.pid)

        exit_expected = es in self.config.exitcodes

        if self.killing:
            # likely the result of a stop request implies STOPPING -> STOPPED
            self.killing = False
            self.delay = 0
            self.exitstatus = es

            fmt, args = 'stopped: %s (%s)', (processname, msg)
            self._check_in_state(ProcessStates.STOPPING)
            self.change_state(ProcessStates.STOPPED)
            if exit_expected:
                log.info(fmt, *args)
            else:
                log.warning(fmt, *args)

        elif too_quickly:
            # the program did not stay up long enough to make it to RUNNING implies STARTING -> BACKOFF
            self.exitstatus = None
            self.spawn_err = 'Exited too quickly (process log may have details)'
            self._check_in_state(ProcessStates.STARTING)
            self.change_state(ProcessStates.BACKOFF)
            log.warning('exited: %s (%s)', processname, msg + '; not expected')

        else:
            # this finish was not the result of a stop request, the program was in the RUNNING state but exited implies
            # RUNNING -> EXITED normally but see next comment
            self.delay = 0
            self.backoff = 0
            self.exitstatus = es

            # if the process was STARTING but a system time change causes self.laststart to be in the future, the normal
            # STARTING->RUNNING transition can be subverted so we perform the transition here.
            if self.state == ProcessStates.STARTING:
                self.change_state(ProcessStates.RUNNING)

            self._check_in_state(ProcessStates.RUNNING)

            if exit_expected:
                # expected exit code
                self.change_state(ProcessStates.EXITED, expected=True)
                log.info('exited: %s (%s)', processname, msg + '; expected')
            else:
                # unexpected exit code
                self.spawn_err = f'Bad exit code {es}'
                self.change_state(ProcessStates.EXITED, expected=False)
                log.warning('exited: %s (%s)', processname, msg + '; not expected')

        self._pid = 0
        close_parent_pipes(self._pipes)
        self._pipes = {}
        self._dispatchers = {}

        # if we died before we processed the current event (only happens if we're an event listener), notify the event
        # system that this event was rejected so it can be processed again.
        if self.event is not None:
            # Note: this should only be true if we were in the BUSY state when finish() was called.
            notify_event(EventRejectedEvent(self, self.event))  # type: ignore
            self.event = None

    def set_uid(self) -> ta.Optional[str]:
        if self.config.uid is None:
            return None
        msg = drop_privileges(self.config.uid)
        return msg

    def __lt__(self, other):
        return self.config.priority < other.config.priority

    def __eq__(self, other):
        return self.config.priority == other.config.priority

    def __repr__(self):
        # repr can't return anything other than a native string, but the name might be unicode - a problem on Python 2.
        name = self.config.name
        return f'<Subprocess at {id(self)} with name {name} in state {get_process_state_description(self.get_state())}>'

    def get_state(self) -> ProcessState:
        return self.state

    def transition(self):
        now = time.time()
        state = self.state

        self._check_and_adjust_for_system_clock_rollback(now)

        logger = log

        if self.context.state > SupervisorStates.RESTARTING:
            # dont start any processes if supervisor is shutting down
            if state == ProcessStates.EXITED:
                if self.config.autorestart:
                    if self.config.autorestart is RestartUnconditionally:
                        # EXITED -> STARTING
                        self.spawn()
                    elif self.exitstatus not in self.config.exitcodes:  # type: ignore
                        # EXITED -> STARTING
                        self.spawn()

            elif state == ProcessStates.STOPPED and not self.laststart:
                if self.config.autostart:
                    # STOPPED -> STARTING
                    self.spawn()

            elif state == ProcessStates.BACKOFF:
                if self.backoff <= self.config.startretries:
                    if now > self.delay:
                        # BACKOFF -> STARTING
                        self.spawn()

        processname = as_string(self.config.name)
        if state == ProcessStates.STARTING:
            if now - self.laststart > self.config.startsecs:
                # STARTING -> RUNNING if the proc has started successfully and it has stayed up for at least
                # proc.config.startsecs,
                self.delay = 0
                self.backoff = 0
                self._check_in_state(ProcessStates.STARTING)
                self.change_state(ProcessStates.RUNNING)
                msg = ('entered RUNNING state, process has stayed up for > than %s seconds (startsecs)' % self.config.startsecs)  # noqa
                logger.info('success: %s %s', processname, msg)

        if state == ProcessStates.BACKOFF:
            if self.backoff > self.config.startretries:
                # BACKOFF -> FATAL if the proc has exceeded its number of retries
                self.give_up()
                msg = ('entered FATAL state, too many start retries too quickly')
                logger.info('gave up: %s %s', processname, msg)

        elif state == ProcessStates.STOPPING:
            time_left = self.delay - now
            if time_left <= 0:
                # kill processes which are taking too long to stop with a final sigkill.  if this doesn't kill it, the
                # process will be stuck in the STOPPING state forever.
                log.warning('killing \'%s\' (%s) with SIGKILL', processname, self.pid)
                self.kill(signal.SIGKILL)

    def create_auto_child_logs(self):
        # temporary logfiles which are erased at start time
        # get_autoname = self.context.get_auto_child_log_name  # noqa
        # sid = self.context.config.identifier  # noqa
        # name = self.config.name  # noqa
        # if self.stdout_logfile is Automatic:
        #     self.stdout_logfile = get_autoname(name, sid, 'stdout')
        # if self.stderr_logfile is Automatic:
        #     self.stderr_logfile = get_autoname(name, sid, 'stderr')
        pass


@functools.total_ordering
class ProcessGroup:
    def __init__(self, config: ProcessGroupConfig, context: ServerContext):
        super().__init__()
        self.config = config
        self.context = context
        self.processes = {}
        for pconfig in self.config.processes or []:
            process = Subprocess(pconfig, self, self.context)
            self.processes[pconfig.name] = process

    def __lt__(self, other):
        return self.config.priority < other.config.priority

    def __eq__(self, other):
        return self.config.priority == other.config.priority

    def __repr__(self):
        # repr can't return anything other than a native string, but the name might be unicode - a problem on Python 2.
        name = self.config.name
        return f'<{self.__class__.__name__} instance at {id(self)} named {name}>'

    def remove_logs(self) -> None:
        for process in self.processes.values():
            process.remove_logs()

    def reopen_logs(self) -> None:
        for process in self.processes.values():
            process.reopen_logs()

    def stop_all(self) -> None:
        processes = list(self.processes.values())
        processes.sort()
        processes.reverse()  # stop in desc priority order

        for proc in processes:
            state = proc.get_state()
            if state == ProcessStates.RUNNING:
                # RUNNING -> STOPPING
                proc.stop()

            elif state == ProcessStates.STARTING:
                # STARTING -> STOPPING
                proc.stop()

            elif state == ProcessStates.BACKOFF:
                # BACKOFF -> FATAL
                proc.give_up()

    def get_unstopped_processes(self) -> ta.List[Subprocess]:
        return [x for x in self.processes.values() if x.get_state() not in STOPPED_STATES]

    def get_dispatchers(self) -> ta.Dict[int, Dispatcher]:
        dispatchers = {}
        for process in self.processes.values():
            dispatchers.update(process._dispatchers)  # noqa
        return dispatchers

    def before_remove(self) -> None:
        pass

    def transition(self) -> None:
        for proc in self.processes.values():
            proc.transition()

    def after_setuid(self) -> None:
        for proc in self.processes.values():
            proc.create_auto_child_logs()


########################################
# supervisor.py


log = logging.getLogger(__name__)


class Supervisor:

    def __init__(self, context: ServerContext) -> None:
        super().__init__()

        self._context = context
        self._ticks: ta.Dict[int, float] = {}
        self._process_groups: ta.Dict[str, ProcessGroup] = {}  # map of process group name to process group object
        self._stop_groups: ta.Optional[ta.List[ProcessGroup]] = None  # list used for priority ordered shutdown
        self._stopping = False  # set after we detect that we are handling a stop request
        self._last_shutdown_report = 0.  # throttle for delayed process error reports at stop

    @property
    def context(self) -> ServerContext:
        return self._context

    def get_state(self) -> SupervisorState:
        return self._context.state

    def main(self) -> None:
        if not self._context.first:
            # prevent crash on libdispatch-based systems, at least for the first request
            self._context.cleanup_fds()

        self._context.set_uid_or_exit()

        if self._context.first:
            self._context.set_rlimits_or_exit()

        # this sets the options.logger object delay logger instantiation until after setuid
        if not self._context.config.nocleanup:
            # clean up old automatic logs
            self._context.clear_auto_child_logdir()

        self.run()

    def run(self) -> None:
        self._process_groups = {}  # clear
        self._stop_groups = None  # clear

        clear_events()

        try:
            for config in self._context.config.groups or []:
                self.add_process_group(config)

            self._context.set_signals()

            if not self._context.config.nodaemon and self._context.first:
                self._context.daemonize()

            # writing pid file needs to come *after* daemonizing or pid will be wrong
            self._context.write_pidfile()

            self.runforever()

        finally:
            self._context.cleanup()

    def diff_to_active(self):
        new = self._context.config.groups or []
        cur = [group.config for group in self._process_groups.values()]

        curdict = dict(zip([cfg.name for cfg in cur], cur))
        newdict = dict(zip([cfg.name for cfg in new], new))

        added = [cand for cand in new if cand.name not in curdict]
        removed = [cand for cand in cur if cand.name not in newdict]

        changed = [cand for cand in new if cand != curdict.get(cand.name, cand)]

        return added, changed, removed

    def add_process_group(self, config: ProcessGroupConfig) -> bool:
        name = config.name
        if name in self._process_groups:
            return False

        group = self._process_groups[name] = ProcessGroup(config, self._context)
        group.after_setuid()

        notify_event(ProcessGroupAddedEvent(name))
        return True

    def remove_process_group(self, name: str) -> bool:
        if self._process_groups[name].get_unstopped_processes():
            return False

        self._process_groups[name].before_remove()

        del self._process_groups[name]

        notify_event(ProcessGroupRemovedEvent(name))
        return True

    def get_process_map(self) -> ta.Dict[int, Dispatcher]:
        process_map = {}
        for group in self._process_groups.values():
            process_map.update(group.get_dispatchers())
        return process_map

    def shutdown_report(self) -> ta.List[Subprocess]:
        unstopped: ta.List[Subprocess] = []

        for group in self._process_groups.values():
            unstopped.extend(group.get_unstopped_processes())

        if unstopped:
            # throttle 'waiting for x to die' reports
            now = time.time()
            if now > (self._last_shutdown_report + 3):  # every 3 secs
                names = [as_string(p.config.name) for p in unstopped]
                namestr = ', '.join(names)
                log.info('waiting for %s to die', namestr)
                self._last_shutdown_report = now
                for proc in unstopped:
                    state = get_process_state_description(proc.get_state())
                    log.debug('%s state: %s', proc.config.name, state)

        return unstopped

    def _ordered_stop_groups_phase_1(self) -> None:
        if self._stop_groups:
            # stop the last group (the one with the "highest" priority)
            self._stop_groups[-1].stop_all()

    def _ordered_stop_groups_phase_2(self) -> None:
        # after phase 1 we've transitioned and reaped, let's see if we can remove the group we stopped from the
        # stop_groups queue.
        if self._stop_groups:
            # pop the last group (the one with the "highest" priority)
            group = self._stop_groups.pop()
            if group.get_unstopped_processes():
                # if any processes in the group aren't yet in a stopped state, we're not yet done shutting this group
                # down, so push it back on to the end of the stop group queue
                self._stop_groups.append(group)

    def runforever(self) -> None:
        notify_event(SupervisorRunningEvent())
        timeout = 1  # this cannot be fewer than the smallest TickEvent (5)

        while True:
            combined_map = {}
            combined_map.update(self.get_process_map())

            pgroups = list(self._process_groups.values())
            pgroups.sort()

            if self._context.state < SupervisorStates.RUNNING:
                if not self._stopping:
                    # first time, set the stopping flag, do a notification and set stop_groups
                    self._stopping = True
                    self._stop_groups = pgroups[:]
                    notify_event(SupervisorStoppingEvent())

                self._ordered_stop_groups_phase_1()

                if not self.shutdown_report():
                    # if there are no unstopped processes (we're done killing everything), it's OK to shutdown or reload
                    raise ExitNow

            for fd, dispatcher in combined_map.items():
                if dispatcher.readable():
                    self._context.poller.register_readable(fd)
                if dispatcher.writable():
                    self._context.poller.register_writable(fd)

            r, w = self._context.poller.poll(timeout)

            for fd in r:
                if fd in combined_map:
                    try:
                        dispatcher = combined_map[fd]
                        log.debug('read event caused by %r', dispatcher)
                        dispatcher.handle_read_event()
                        if not dispatcher.readable():
                            self._context.poller.unregister_readable(fd)
                    except ExitNow:
                        raise
                    except Exception:  # noqa
                        combined_map[fd].handle_error()
                else:
                    # if the fd is not in combined_map, we should unregister it. otherwise, it will be polled every
                    # time, which may cause 100% cpu usage
                    log.debug('unexpected read event from fd %r', fd)
                    try:
                        self._context.poller.unregister_readable(fd)
                    except Exception:  # noqa
                        pass

            for fd in w:
                if fd in combined_map:
                    try:
                        dispatcher = combined_map[fd]
                        log.debug('write event caused by %r', dispatcher)
                        dispatcher.handle_write_event()
                        if not dispatcher.writable():
                            self._context.poller.unregister_writable(fd)
                    except ExitNow:
                        raise
                    except Exception:  # noqa
                        combined_map[fd].handle_error()
                else:
                    log.debug('unexpected write event from fd %r', fd)
                    try:
                        self._context.poller.unregister_writable(fd)
                    except Exception:  # noqa
                        pass

            for group in pgroups:
                group.transition()

            self._reap()
            self._handle_signal()
            self._tick()

            if self._context.state < SupervisorStates.RUNNING:
                self._ordered_stop_groups_phase_2()

            if self._context.test:
                break

    def _tick(self, now: ta.Optional[float] = None) -> None:
        """Send one or more 'tick' events when the timeslice related to the period for the event type rolls over"""

        if now is None:
            # now won't be None in unit tests
            now = time.time()

        for event in TICK_EVENTS:
            period = event.period  # type: ignore

            last_tick = self._ticks.get(period)
            if last_tick is None:
                # we just started up
                last_tick = self._ticks[period] = timeslice(period, now)

            this_tick = timeslice(period, now)
            if this_tick != last_tick:
                self._ticks[period] = this_tick
                notify_event(event(this_tick, self))

    def _reap(self, *, once: bool = False, depth: int = 0) -> None:
        if depth >= 100:
            return

        pid, sts = self._context.waitpid()
        if not pid:
            return

        process = self._context.pid_history.get(pid, None)
        if process is None:
            _, msg = decode_wait_status(check_not_none(sts))
            log.info('reaped unknown pid %s (%s)', pid, msg)
        else:
            process.finish(check_not_none(sts))
            del self._context.pid_history[pid]

        if not once:
            # keep reaping until no more kids to reap, but don't recurse infinitely
            self._reap(once=False, depth=depth + 1)

    def _handle_signal(self) -> None:
        sig = self._context.get_signal()
        if not sig:
            return

        if sig in (signal.SIGTERM, signal.SIGINT, signal.SIGQUIT):
            log.warning('received %s indicating exit request', signame(sig))
            self._context.set_state(SupervisorStates.SHUTDOWN)

        elif sig == signal.SIGHUP:
            if self._context.state == SupervisorStates.SHUTDOWN:
                log.warning('ignored %s indicating restart request (shutdown in progress)', signame(sig))  # noqa
            else:
                log.warning('received %s indicating restart request', signame(sig))  # noqa
                self._context.set_state(SupervisorStates.RESTARTING)

        elif sig == signal.SIGCHLD:
            log.debug('received %s indicating a child quit', signame(sig))

        elif sig == signal.SIGUSR2:
            log.info('received %s indicating log reopen request', signame(sig))
            # self._context.reopen_logs()
            for group in self._process_groups.values():
                group.reopen_logs()

        else:
            log.debug('received %s indicating nothing', signame(sig))


def timeslice(period, when):
    return int(when - (when % period))


def main(args=None, test=False):
    configure_standard_logging('INFO')

    # if we hup, restart by making a new Supervisor()
    first = True
    while True:
        config = ServerConfig.new(
            nodaemon=True,
            groups=[
                ProcessGroupConfig(
                    name='default',
                    processes=[
                        ProcessConfig(
                            name='sleep',
                            command='sleep 600',
                            stdout=ProcessConfig.Log(
                                file='/dev/fd/1',
                                maxbytes=0,
                            ),
                            redirect_stderr=True,
                        ),
                        ProcessConfig(
                            name='ls',
                            command='ls -al',
                            stdout=ProcessConfig.Log(
                                file='/dev/fd/1',
                                maxbytes=0,
                            ),
                            redirect_stderr=True,
                        ),
                    ],
                ),
            ],
        )

        context = ServerContext(
            config,
        )

        context.first = first
        context.test = test
        go(context)
        # options.close_logger()
        first = False
        if test or (context.state < SupervisorStates.RESTARTING):
            break


def go(context):  # pragma: no cover
    d = Supervisor(context)
    try:
        d.main()
    except ExitNow:
        pass


if __name__ == '__main__':
    main()
