#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omdev-amalg-output supervisord.py
"""
TODO:
 - amalg or not? only use om.logs and dc's
"""
import dataclasses as dc
import errno
import fcntl
import functools
import grp
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
import time
import traceback
import types
import typing as ta
import warnings


T = ta.TypeVar('T')


########################################
# ../../../../omdev/amalg/std/logs.py
"""
TODO:
 - debug
"""


log = logging.getLogger(__name__)


def setup_standard_logging(level: ta.Union[int, str] = logging.INFO) -> None:
    logging.root.addHandler(logging.StreamHandler())
    logging.root.setLevel(level)


########################################
# ../compat.py


def as_bytes(s: str | bytes, encoding: str = 'utf8') -> bytes:
    if isinstance(s, bytes):
        return s
    else:
        return s.encode(encoding)


def as_string(s: str | bytes, encoding='utf8') -> str:
    if isinstance(s, str):
        return s
    else:
        return s.decode(encoding)


def compact_traceback() -> tuple[tuple[str, str, int], type[BaseException], BaseException, types.TracebackType]:
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
    info = ' '.join(['[%s|%s|%s]' % x for x in tbinfo])
    return (file, function, line), t, v, info


def find_prefix_at_end(haystack: T, needle: T) -> int:
    l = len(needle) - 1
    while l and not haystack.endswith(needle[:l]):
        l -= 1
    return l


class ExitNow(Exception):
    pass


##


def decode_wait_status(sts: int) -> tuple[int, str]:
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


_signames: ta.Mapping[int, str] | None = None


def signame(sig: int) -> str:
    global _signames
    if _signames is None:
        _signames = _init_signames()
    return _signames.get(sig) or 'signal %d' % sig


def _init_signames() -> dict[int, str]:
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
        self._signals_recvd: list[int] = []

    def receive(self, sig: int, frame: ta.Any) -> None:
        if sig not in self._signals_recvd:
            self._signals_recvd.append(sig)

    def install(self, *sigs: int) -> None:
        for sig in sigs:
            signal.signal(sig, self.receive)

    def get_signal(self) -> int | None:
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


def mktempfile(suffix: str, prefix: str, dir: str) -> str:
    # set os._urandomfd as a hack around bad file descriptor bug seen in the wild, see
    # https://web.archive.org/web/20160729044005/http://www.plope.com/software/collector/252
    os._urandomfd = None
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
    L = len(s)
    while i < L:
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
            raise ValueError('Invalid user name %s' % name)
        uid = pwdrec[2]
    else:
        try:
            pwd.getpwuid(uid)  # check if uid is valid
        except KeyError:
            raise ValueError('Invalid user id %s' % name)
    return uid


def name_to_gid(name: str) -> int:
    try:
        gid = int(name)
    except ValueError:
        try:
            grprec = grp.getgrnam(name)
        except KeyError:
            raise ValueError('Invalid group name %s' % name)
        gid = grprec[2]
    else:
        try:
            grp.getgrgid(gid)  # check if gid is valid
        except KeyError:
            raise ValueError('Invalid group id %s' % name)
    return gid


def gid_for_uid(uid: int) -> int:
    pwrec = pwd.getpwuid(uid)
    return pwrec[3]


def octal_type(arg: str | int) -> int:
    if isinstance(arg, int):
        return arg
    try:
        return int(arg, 8)
    except (TypeError, ValueError):
        raise ValueError('%s can not be converted to an octal type' % arg)


def existing_directory(v: str) -> str:
    nv = os.path.expanduser(v)
    if os.path.isdir(nv):
        return nv
    raise ValueError('%s is not an existing directory' % v)


def existing_dirpath(v: str) -> str:
    nv = os.path.expanduser(v)
    dir = os.path.dirname(nv)
    if not dir:
        # relative pathname with no directory component
        return nv
    if os.path.isdir(dir):
        return nv
    raise ValueError('The directory named as part of the path %s does not exist' % v)


def logging_level(value: str | int) -> int:
    if isinstance(value, int):
        return value
    s = str(value).lower()
    level = logging.getLevelNamesMapping().get(s.upper())
    if level is None:
        raise ValueError('bad logging level name %r' % value)
    return level


class SuffixMultiplier:
    # d is a dictionary of suffixes to integer multipliers.  If no suffixes match, default is the multiplier.  Matches
    # are case insensitive.  Return values are in the fundamental unit.
    def __init__(self, d, default=1):
        self._d = d
        self._default = default
        # all keys must be the same size
        self._keysz = None
        for k in d.keys():
            if self._keysz is None:
                self._keysz = len(k)
            else:
                if self._keysz != len(k):
                    raise ValueError(k)

    def __call__(self, v: str | int) -> int:
        if isinstance(v, int):
            return v
        v = v.lower()
        for s, m in self._d.items():
            if v[-self._keysz:] == s:
                return int(v[:-self._keysz]) * m
        return int(v) * self._default


byte_size = SuffixMultiplier({
    'kb': 1024,
    'mb': 1024 * 1024,
    'gb': 1024 * 1024 * 1024,
})


# all valid signal numbers
SIGNUMS = [getattr(signal, k) for k in dir(signal) if k.startswith('SIG')]


def signal_number(value: int | str) -> int:
    try:
        num = int(value)
    except (ValueError, TypeError):
        name = value.strip().upper()
        if not name.startswith('SIG'):
            name = 'SIG' + name
        num = getattr(signal, name, None)
        if num is None:
            raise ValueError('value %r is not a valid signal name' % value)
    if num not in SIGNUMS:
        raise ValueError('value %r is not a valid signal number' % value)
    return num


class RestartWhenExitUnexpected:
    pass


class RestartUnconditionally:
    pass


########################################
# ../exceptions.py


class ProcessException(Exception):
    """ Specialized exceptions used when attempting to start a process """


class BadCommand(ProcessException):
    """ Indicates the command could not be parsed properly. """


class NotExecutable(ProcessException):
    """ Indicates that the filespec cannot be executed because its path
    resolves to a file which is not executable, or which is a directory. """


class NotFound(ProcessException):
    """ Indicates that the filespec cannot be executed because it could not be found """


class NoPermission(ProcessException):
    """
    Indicates that the file cannot be executed because the supervisor process does not possess the appropriate UNIX
    filesystem permission to execute the file.
    """


########################################
# ../poller.py


log = logging.getLogger(__name__)


class BasePoller:

    def __init__(self) -> None:
        super().__init__()

    def register_readable(self, fd: int) -> None:
        raise NotImplementedError

    def register_writable(self, fd: int) -> None:
        raise NotImplementedError

    def unregister_readable(self, fd: int) -> None:
        raise NotImplementedError

    def unregister_writable(self, fd: int) -> None:
        raise NotImplementedError

    def poll(self, timeout: float | None) -> tuple[list[int], list[int]]:
        raise NotImplementedError

    def before_daemonize(self) -> None:
        pass

    def after_daemonize(self) -> None:
        pass

    def close(self) -> None:
        pass


class SelectPoller(BasePoller):

    def __init__(self) -> None:
        super().__init__()

        self._readables: set[int] = set()
        self._writables: set[int] = set()

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

    def poll(self, timeout: float | None) -> tuple[list[int], list[int]]:
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

    def poll(self, timeout: float | None) -> tuple[list[int], list[int]]:
        fds = self._poll_fds(timeout)
        readables, writables = [], []
        for fd, eventmask in fds:
            if self._ignore_invalid(fd, eventmask):
                continue
            if eventmask & self._READ:
                readables.append(fd)
            if eventmask & self._WRITE:
                writables.append(fd)
        return readables, writables

    def _poll_fds(self, timeout: float) -> list[tuple[int, int]]:
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


class KQueuePoller(BasePoller):
    max_events = 1000

    def __init__(self) -> None:
        super().__init__()

        self._kqueue = select.kqueue()
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
            self._kqueue.control([kevent], 0)
        except OSError as error:
            if error.errno == errno.EBADF:
                log.debug('EBADF encountered in kqueue. Invalid file descriptor %s' % fd)
            else:
                raise

    def poll(self, timeout: float | None) -> tuple[list[int], list[int]]:
        readables, writables = [], []

        try:
            kevents = self._kqueue.control(None, self.max_events, timeout)
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
        self._kqueue.close()
        self._kqueue = None


if hasattr(select, 'kqueue'):
    Poller = KQueuePoller
elif hasattr(select, 'poll'):
    Poller = PollPoller
else:
    Poller = SelectPoller


########################################
# ../states.py


##


def _names_by_code(states: ta.Any) -> dict[int, str]:
    d = {}
    for name in states.__dict__:
        if not name.startswith('__'):
            code = getattr(states, name)
            d[code] = name
    return d


##


ProcessState: ta.TypeAlias = int


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
    return _process_states_by_code.get(code)


##


SupervisorState: ta.TypeAlias = int


class SupervisorStates:
    FATAL = 2
    RUNNING = 1
    RESTARTING = 0
    SHUTDOWN = -1


_supervisor_states_by_code = _names_by_code(SupervisorStates)


def get_supervisor_state_description(code: SupervisorState) -> str:
    return _supervisor_states_by_code.get(code)


########################################
# ../configs.py


@dc.dataclass(frozen=True)
class ServerConfig:
    user: str | None = None
    nodaemon: bool = False
    umask: int = 0o22
    directory: str | None = None
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

    groups: ta.Sequence['ProcessGroupConfig'] | None = None

    @classmethod
    def new(
            cls,
            umask: int | str = 0o22,
            directory: str | None = None,
            logfile: str = 'supervisord.log',
            logfile_maxbytes: int | str = 50 * 1024 * 1024,
            loglevel: int | str = logging.INFO,
            pidfile: str = 'supervisord.pid',
            child_logdir: str | None = None,
            **kwargs: ta.Any
    ) -> 'ServerConfig':
        return cls(
            umask=octal_type(umask),
            directory=existing_directory(directory) if directory is not None else None,
            logfile=existing_dirpath(logfile),
            logfile_maxbytes=byte_size(logfile_maxbytes),
            loglevel=logging_level(loglevel),
            pidfile=existing_dirpath(pidfile),
            child_logdir=tempfile.gettempdir() if not child_logdir else child_logdir,
            **kwargs,
        )


@dc.dataclass(frozen=True)
class ProcessGroupConfig:
    name: str

    priority: int = 999

    processes: ta.Sequence['ProcessConfig'] | None = None


@dc.dataclass(frozen=True)
class ProcessConfig:
    name: str
    command: str

    uid: int | None = None
    directory: str | None = None
    umask: int | None = None
    priority: int = 999

    autostart: bool = True
    autorestart: str = 'unexpected'

    startsecs: int = 1
    startretries: int = 3

    numprocs: int = 1
    numprocs_start: int = 0

    @dc.dataclass(frozen=True)
    class Log:
        file: str | None = None
        capture_maxbytes: int | None = None
        events_enabled: bool = False
        syslog: bool = False
        backups: int | None = None
        maxbytes: int | None = None

    stdout: Log = Log()
    stderr: Log = Log()

    stopsignal: int = signal.SIGTERM
    stopwaitsecs: int = 10
    stopasgroup: bool = False

    killasgroup: bool = False

    exitcodes: ta.Iterable[int] = (0,)

    redirect_stderr: bool = False

    environment: ta.Mapping[str, str] | None = None


########################################
# ../events.py


callbacks = []


def subscribe(type, callback):
    callbacks.append((type, callback))


def unsubscribe(type, callback):
    callbacks.remove((type, callback))


def notify_event(event):
    for type, callback in callbacks:
        if isinstance(event, type):
            callback(event)


def clear_events():
    callbacks[:] = []


class Event:
    """Abstract event type """


class ProcessLogEvent(Event):
    """Abstract"""
    channel = None

    def __init__(self, process, pid, data):
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
            data = 'Undecodable: %r' % self.data
        fmt = as_string('processname:%s groupname:%s pid:%s channel:%s\n%s')
        result = fmt % (as_string(self.process.config.name),
                        as_string(groupname), self.pid,
                        as_string(self.channel), data)
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
            data = 'Undecodable: %r' % self.data
        return 'processname:%s groupname:%s pid:%s\n%s' % (
            self.process.config.name,
            groupname,
            self.pid,
            data)


class ProcessCommunicationStdoutEvent(ProcessCommunicationEvent):
    channel = 'stdout'


class ProcessCommunicationStderrEvent(ProcessCommunicationEvent):
    channel = 'stderr'


class RemoteCommunicationEvent(Event):
    def __init__(self, type, data):
        self.type = type
        self.data = data

    def payload(self):
        return 'type:%s\n%s' % (self.type, self.data)


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
        self.process = process
        self.event = event


class ProcessStateEvent(Event):
    """ Abstract class, never raised directly """
    frm = None
    to = None

    def __init__(self, process, from_state, expected=True):
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
        L = [
            ('processname', self.process.config.name),
            ('groupname', groupname),
            ('from_state', get_process_state_description(self.from_state)),
        ]
        L.extend(self.extra_values)
        s = ' '.join(['%s:%s' % (name, val) for (name, val) in L])
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
        self.group = group

    def payload(self):
        return 'groupname:%s\n' % self.group


class ProcessGroupAddedEvent(ProcessGroupEvent):
    pass


class ProcessGroupRemovedEvent(ProcessGroupEvent):
    pass


class TickEvent(Event):
    """ Abstract """

    def __init__(self, when, supervisord):
        self.when = when
        self.supervisord = supervisord

    def payload(self):
        return 'when:%s' % self.when


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


def register(name, event):
    setattr(EventTypes, name, event)


########################################
# ../context.py


if ta.TYPE_CHECKING:
    from .process import Subprocess


log = logging.getLogger(__name__)


class ServerContext:
    first = False
    test = False

    ##

    def __init__(self, config: ServerConfig) -> None:
        super().__init__()

        self.config = config

        self.pid_history: dict[int, 'Subprocess'] = {}
        self.state: SupervisorState = SupervisorStates.RUNNING

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

    def waitpid(self) -> tuple[int | None, int | None]:
        # Need pthread_sigmask here to avoid concurrent sigchld, but Python doesn't offer in Python < 3.4.  There is
        # still a race condition here; we can get a sigchld while we're sitting in the waitpid call. However, AFAICT, if
        # waitpid is interrupted by SIGCHLD, as long as we call waitpid again (which happens every so often during the
        # normal course in the mainloop), we'll eventually reap the child that we tried to reap during the interrupted
        # call. At least on Linux, this appears to be true, or at least stopping 50 processes at once never left zombies
        # laying around.
        try:
            pid, sts = os.waitpid(-1, os.WNOHANG)
        except OSError as exc:
            code = exc.args[0]
            if code not in (errno.ECHILD, errno.EINTR):
                log.critical('waitpid error %r; a process may not be cleaned up properly' % code)
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
                    'this message.'
                )
        else:
            msg = drop_privileges(self.uid)
            if msg is None:
                log.info('Set uid to user %s succeeded' % self.uid)
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
            name = name  # name is used below by locals()

            soft, hard = resource.getrlimit(res)

            if (soft < min_limit) and (soft != -1):  # -1 means unlimited
                if (hard < min_limit) and (hard != -1):
                    # setrlimit should increase the hard limit if we are root, if not then setrlimit raises and we print
                    # usage
                    hard = min_limit

                try:
                    resource.setrlimit(res, (min_limit, hard))
                    log.info('Increased %(name)s limit to %(min_limit)s' % locals())
                except (resource.error, ValueError):
                    raise RuntimeError(msg % locals())

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
        fnre = re.compile(r'.+?---%s-\S+\.log\.{0,1}\d{0,4}' % self.config.identifier)
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
                    log.warning('Failed to clean up %r' % pathname)

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
                log.critical("can't chdir into %r: %s" % (self.config.directory, err))
            else:
                log.info('set current directory: %r' % (self.config.directory),)
        dn = os.open('/dev/null')
        os.dup2(0, dn)
        os.dup2(1, dn)
        os.dup2(2, dn)
        os.setsid()
        os.umask(self.config.umask)
        # XXX Stevens, in his Advanced Unix book, section 13.3 (page 417) recommends calling umask(0) and closing unused
        # file descriptors.  In his Network Programming book, he additionally recommends ignoring SIGHUP and forking
        # again after the setsid() call, for obscure SVR4 reasons.

    def get_auto_child_log_name(self, name: str, identifier: str, channel: str) -> str:
        prefix = '%s-%s---%s-' % (name, channel, identifier)
        logfile = mktempfile(
            suffix='.log',
            prefix=prefix,
            dir=self.config.child_logdir,
        )
        return logfile

    def get_signal(self) -> int | None:
        return self.signal_receiver.get_signal()

    def write_pidfile(self) -> None:
        pid = os.getpid()
        try:
            with open(self.config.pidfile, 'w') as f:
                f.write('%s\n' % pid)
        except OSError:
            log.critical('could not write pidfile %s' % (self.config.pidfile,))
        else:
            self.unlink_pidfile = True
            log.info('supervisord started with pid %s' % pid)


def drop_privileges(user: int | str) -> str | None:
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
            pwrec = pwd.getpwnam(user)
        except KeyError:
            return "Can't find username %r" % user
        uid = pwrec[2]
    else:
        try:
            pwrec = pwd.getpwuid(uid)
        except KeyError:
            return "Can't find uid %r" % uid

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


def make_pipes(stderr=True) -> ta.Mapping[str, int]:
    """
    Create pipes for parent to child stdin/stdout/stderr communications.  Open fd in non-blocking mode so we can
    read them in the mainloop without blocking.  If stderr is False, don't create a pipe for stderr.
    """

    pipes = {
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
        return pipes
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
        raise NotFound("can't find command %r" % filename)

    elif stat.S_ISDIR(st[stat.ST_MODE]):
        raise NotExecutable('command at %r is a directory' % filename)

    elif not (stat.S_IMODE(st[stat.ST_MODE]) & 0o111):
        raise NotExecutable('command at %r is not executable' % filename)

    elif not os.access(filename, os.X_OK):
        raise NoPermission('no permission to run command %r' % filename)


########################################
# ../dispatchers.py


if ta.TYPE_CHECKING:
    from .process import Subprocess


log = logging.getLogger(__name__)


class Dispatcher:

    def __init__(self, process: 'Subprocess', channel: str, fd: int) -> None:
        super().__init__()

        self.process = process  # process which "owns" this dispatcher
        self.channel = channel  # 'stderr' or 'stdout'
        self.fd = fd
        self.closed = False  # True if close() has been called

    def __repr__(self) -> str:
        return '<%s at %s for %s (%s)>' % (self.__class__.__name__, id(self), self.process, self.channel)

    def readable(self):
        raise NotImplementedError

    def writable(self):
        raise NotImplementedError

    def handle_read_event(self):
        raise NotImplementedError

    def handle_write_event(self):
        raise NotImplementedError

    def handle_error(self):
        nil, t, v, tbinfo = compact_traceback()

        log.critical(
            'uncaptured python exception, closing channel %s (%s:%s %s)' % (repr(self), t, v, tbinfo),
        )
        self.close()

    def close(self):
        if not self.closed:
            log.debug('fd %s closed, stopped monitoring %s' % (self.fd, self))
            self.closed = True

    def flush(self):
        pass


class OutputDispatcher(Dispatcher):
    """
    Dispatcher for one channel (stdout or stderr) of one process. Serves several purposes:

    - capture output sent within <!--XSUPERVISOR:BEGIN--> and <!--XSUPERVISOR:END--> tags and signal a
      ProcessCommunicationEvent by calling notify_event(event).
    - route the output to the appropriate log handlers as specified in the config.
    """

    child_log = None  # the current logger (normal_log or capture_log)
    normal_log = None  # the "normal" (non-capture) logger
    capture_log = None  # the logger used while we're in capture_mode
    capture_mode = False  # are we capturing process event data
    output_buffer = b''  # data waiting to be logged

    def __init__(self, process: 'Subprocess', event_type, fd):
        """
        Initialize the dispatcher.

        `event_type` should be one of ProcessLogStdoutEvent or ProcessLogStderrEvent
        """
        super().__init__(process, event_type.channel, fd)
        self.event_type = event_type

        self.lc: ProcessConfig.Log = getattr(process.config, self.channel)

        self._init_normal_log()
        self._init_capture_log()

        self.child_log = self.normal_log

        # all code below is purely for minor speedups
        begin_token = self.event_type.BEGIN_TOKEN
        end_token = self.event_type.END_TOKEN
        self.begin_token_data = (begin_token, len(begin_token))
        self.end_token_data = (end_token, len(end_token))
        self.main_log_level = logging.DEBUG
        config = self.process.config
        self.log_to_main_log = process.context.config.loglevel <= self.main_log_level
        self.stdout_events_enabled = config.stdout.events_enabled
        self.stderr_events_enabled = config.stderr.events_enabled

    def _init_normal_log(self):
        """
        Configure the "normal" (non-capture) log for this channel of this process. Sets self.normal_log if logging is
        enabled.
        """
        config = self.process.config
        channel = self.channel

        logfile = self.lc.file
        maxbytes = self.lc.maxbytes
        backups = self.lc.backups
        to_syslog = self.lc.syslog

        if logfile or to_syslog:
            self.normal_log = logging.getLogger(__name__)

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

    def _init_capture_log(self):
        """
        Configure the capture log for this process.  This log is used to temporarily capture output when special output
        is detected. Sets self.capture_log if capturing is enabled.
        """
        capture_maxbytes = self.lc.capture_maxbytes
        if capture_maxbytes:
            self.capture_log = logging.getLogger(__name__)
            # loggers.handle_boundIO(
            #     self.capture_log,
            #     fmt='%(message)s',
            #     maxbytes=capture_maxbytes,
            # )

    def remove_logs(self):
        for log in (self.normal_log, self.capture_log):
            if log is not None:
                for handler in log.handlers:
                    handler.remove()
                    handler.reopen()

    def reopen_logs(self):
        for log in (self.normal_log, self.capture_log):
            if log is not None:
                for handler in log.handlers:
                    handler.reopen()

    def _log(self, data):
        if data:
            if self.process.context.config.strip_ansi:
                data = strip_escapes(data)
            if self.child_log:
                self.child_log.info(data)
            if self.log_to_main_log:
                if not isinstance(data, bytes):
                    text = data
                else:
                    try:
                        text = data.decode('utf-8')
                    except UnicodeDecodeError:
                        text = 'Undecodable: %r' % data
                msg = '%(name)r %(channel)s output:\n%(data)s'
                log.log(
                    self.main_log_level, msg, name=self.process.config.name,
                    channel=self.channel, data=text)
            if self.channel == 'stdout':
                if self.stdout_events_enabled:
                    notify_event(ProcessLogStdoutEvent(self.process, self.process.pid, data))
            elif self.stderr_events_enabled:
                notify_event(ProcessLogStderrEvent(self.process, self.process.pid, data))

    def record_output(self):
        if self.capture_log is None:
            # shortcut trying to find capture data
            data = self.output_buffer
            self.output_buffer = b''
            self._log(data)
            return

        if self.capture_mode:
            token, tokenlen = self.end_token_data
        else:
            token, tokenlen = self.begin_token_data

        if len(self.output_buffer) <= tokenlen:
            return  # not enough data

        data = self.output_buffer
        self.output_buffer = b''

        try:
            before, after = data.split(token, 1)
        except ValueError:
            after = None
            index = find_prefix_at_end(data, token)
            if index:
                self.output_buffer = self.output_buffer + data[-index:]
                data = data[:-index]
            self._log(data)
        else:
            self._log(before)
            self.toggle_capture_mode()
            self.output_buffer = after

        if after:
            self.record_output()

    def toggle_capture_mode(self):
        self.capture_mode = not self.capture_mode

        if self.capture_log is not None:
            if self.capture_mode:
                self.child_log = self.capture_log
            else:
                for handler in self.capture_log.handlers:
                    handler.flush()
                data = self.capture_log.getvalue()
                channel = self.channel
                procname = self.process.config.name
                event = self.event_type(self.process, self.process.pid, data)
                notify_event(event)

                msg = '%(procname)r %(channel)s emitted a comm event'
                log.debug(msg, procname=procname, channel=channel)
                for handler in self.capture_log.handlers:
                    handler.remove()
                    handler.reopen()
                self.child_log = self.normal_log

    def writable(self):
        return False

    def readable(self):
        if self.closed:
            return False
        return True

    def handle_read_event(self):
        data = readfd(self.fd)
        self.output_buffer += data
        self.record_output()
        if not data:
            # if we get no data back from the pipe, it means that the child process has ended.  See
            # mail.python.org/pipermail/python-dev/2004-August/046850.html
            self.close()


class InputDispatcher(Dispatcher):

    def __init__(self, process, channel, fd):
        super().__init__(process, channel, fd)
        self.input_buffer = b''

    def writable(self):
        if self.input_buffer and not self.closed:
            return True
        return False

    def readable(self):
        return False

    def flush(self):
        # other code depends on this raising EPIPE if the pipe is closed
        sent = os.write(self.fd, as_bytes(self.input_buffer))
        self.input_buffer = self.input_buffer[sent:]

    def handle_write_event(self):
        if self.input_buffer:
            try:
                self.flush()
            except OSError as why:
                if why.args[0] == errno.EPIPE:
                    self.input_buffer = b''
                    self.close()
                else:
                    raise


########################################
# ../process.py


log = logging.getLogger(__name__)


@functools.total_ordering
class Subprocess:
    """A class to manage a subprocess."""

    # Initial state; overridden by instance variables

    pid = 0  # Subprocess pid; 0 when not running
    config = None  # ProcessConfig instance
    state = None  # process state code
    listener_state = None  # listener state code (if we're an event listener)
    event = None  # event currently being processed (if we're an event listener)
    laststart = 0  # Last time the subprocess was started; 0 if never
    laststop = 0  # Last time the subprocess was stopped; 0 if never
    last_stop_report = 0  # Last time "waiting for x to stop" logged, to throttle
    delay = 0  # If nonzero, delay starting or killing until this time
    administrative_stop = False  # true if process has been stopped by an admin
    system_stop = False  # true if process has been stopped by the system
    killing = False  # true if we are trying to kill this process
    backoff = 0  # backoff counter (to startretries)
    dispatchers = None  # asyncore output dispatchers (keyed by fd)
    pipes = None  # map of channel name to file descriptor #
    exitstatus = None  # status attached to dead process by finish()
    spawn_err = None  # error message attached by spawn() if any
    group = None  # ProcessGroup instance if process is in the group

    def __init__(self, config: ProcessConfig, group: 'ProcessGroup', context: ServerContext) -> None:
        self.config = config
        self.group = group
        self.context = context
        self._dispatchers = {}
        self._pipes = {}
        self.state = ProcessStates.STOPPED

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

    def write(self, chars: bytes | str) -> None:
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

    def _get_execv_args(self) -> tuple[str, ta.Sequence[str]]:
        """
        Internal: turn a program name into a file name, using $PATH, make sure it exists / is executable, raising a
        ProcessException if not
        """
        try:
            commandargs = shlex.split(self.config.command)
        except ValueError as e:
            raise BadCommand("can't parse command %r: %s" % (self.config.command, str(e)))

        if commandargs:
            program = commandargs[0]
        else:
            raise BadCommand('command is empty')

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
            for dir in path:
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
                filename = found

        # check_execv_args will raise a ProcessException if the execv args are bogus, we break it out into a separate
        # options method call here only to service unit tests
        check_execv_args(filename, commandargs, st)

        return filename, commandargs

    event_map = {
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
        log.info('spawn_err: %s' % msg)

    def spawn(self) -> int | None:
        processname = as_string(self.config.name)

        if self.pid:
            msg = 'process \'%s\' already running' % processname
            log.warning(msg)
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
        except ProcessException as what:
            self._record_spawn_err(what.args[0])
            self._check_in_state(ProcessStates.STARTING)
            self.change_state(ProcessStates.BACKOFF)
            return None

        try:
            self._dispatchers, self._pipes = self._make_dispatchers()
        except OSError as why:
            code = why.args[0]
            if code == errno.EMFILE:
                # too many file descriptors open
                msg = 'too many open files to spawn \'%s\'' % processname
            else:
                msg = 'unknown error making dispatchers for \'%s\': %s' % (processname, errno.errorcode.get(code, code))
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
                msg = ('Too many processes in process table to spawn \'%s\'' % processname)
            else:
                msg = 'unknown error during fork for \'%s\': %s' % (processname, errno.errorcode.get(code, code))
            self._record_spawn_err(msg)
            self._check_in_state(ProcessStates.STARTING)
            self.change_state(ProcessStates.BACKOFF)
            close_parent_pipes(self._pipes)
            close_child_pipes(self._pipes)
            return None

        if pid != 0:
            return self._spawn_as_parent(pid)

        else:
            return self._spawn_as_child(filename, argv)

    def _make_dispatchers(self) -> tuple[ta.Mapping[int, Dispatcher], ta.Mapping[str, int]]:
        use_stderr = not self.config.redirect_stderr
        p = make_pipes(use_stderr)
        stdout_fd, stderr_fd, stdin_fd = p['stdout'], p['stderr'], p['stdin']
        dispatchers: dict[int, Dispatcher] = {}
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
        self.pid = pid
        close_child_pipes(self._pipes)
        log.info('spawned: \'%s\' with pid %s' % (as_string(self.config.name), pid))
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
                msg = "couldn't setuid to %s: %s\n" % (uid, setuid_msg)
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
                msg = "couldn't chdir to %s: %s\n" % (cwd, code)
                os.write(2, as_bytes('supervisor: ' + msg))
                return  # finally clause will exit the child process

            # set umask, then execve
            try:
                if self.config.umask is not None:
                    os.umask(self.config.umask)
                os.execve(filename, argv, env)
            except OSError as why:
                code = errno.errorcode.get(why.args[0], why.args[0])
                msg = "couldn't exec %s: %s\n" % (argv[0], code)
                os.write(2, as_bytes('supervisor: ' + msg))
            except:
                (file, fun, line), t, v, tbinfo = compact_traceback()
                error = '%s, %s: file: %s line: %s' % (t, v, file, line)
                msg = "couldn't exec %s: %s\n" % (filename, error)
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
            if test_time < self.laststart:
                self.laststart = test_time
            if self.delay > 0 and test_time < (self.delay - self.config.startsecs):
                self.delay = test_time + self.config.startsecs

        elif self.state == ProcessStates.RUNNING:
            if test_time > self.laststart and test_time < (self.laststart + self.config.startsecs):
                self.laststart = test_time - self.config.startsecs

        elif self.state == ProcessStates.STOPPING:
            if test_time < self.last_stop_report:
                self.last_stop_report = test_time
            if self.delay > 0 and test_time < (self.delay - self.config.stopwaitsecs):
                self.delay = test_time + self.config.stopwaitsecs

        elif self.state == ProcessStates.BACKOFF:
            if self.delay > 0 and test_time < (self.delay - self.backoff):
                self.delay = test_time + self.backoff

    def stop(self) -> str | None:
        self.administrative_stop = True
        self.last_stop_report = 0
        return self.kill(self.config.stopsignal)

    def stop_report(self) -> None:
        """ Log a 'waiting for x to stop' message with throttling. """
        if self.state == ProcessStates.STOPPING:
            now = time.time()

            self._check_and_adjust_for_system_clock_rollback(now)

            if now > (self.last_stop_report + 2):  # every 2 seconds
                log.info('waiting for %s to stop' % as_string(self.config.name))
                self.last_stop_report = now

    def give_up(self) -> None:
        self.delay = 0
        self.backoff = 0
        self.system_stop = True
        self._check_in_state(ProcessStates.BACKOFF)
        self.change_state(ProcessStates.FATAL)

    def kill(self, sig: int) -> str | None:
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
            msg = ('Attempted to kill %s, which is in BACKOFF state.' % processname)
            log.debug(msg)
            self.change_state(ProcessStates.STOPPED)
            return None

        if not self.pid:
            msg = ("attempted to kill %s with sig %s but it wasn't running" % (processname, signame(sig)))
            log.debug(msg)
            return msg

        # If we're in the stopping state, then we've already sent the stop signal and this is the kill signal
        if self.state == ProcessStates.STOPPING:
            killasgroup = self.config.killasgroup
        else:
            killasgroup = self.config.stopasgroup

        as_group = ''
        if killasgroup:
            as_group = 'process group '

        log.debug('killing %s (pid %s) %swith signal %s' % (processname, self.pid, as_group, signame(sig)))

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
                    msg = ('unable to signal %s (pid %s), it probably just exited '
                           'on its own: %s' % (processname, self.pid, str(exc)))
                    log.debug(msg)
                    # we could change the state here but we intentionally do not.  we will do it during normal SIGCHLD
                    # processing.
                    return None
                raise
        except:
            tb = traceback.format_exc()
            msg = 'unknown problem killing %s (%s):%s' % (processname, self.pid, tb)
            log.critical(msg)
            self.change_state(ProcessStates.UNKNOWN)
            self.killing = False
            self.delay = 0
            return msg

        return None

    def signal(self, sig: int) -> str | None:
        """
        Send a signal to the subprocess, without intending to kill it.

        Return None if the signal was sent, or an error message string if an error occurred or if the subprocess is not
        running.
        """
        processname = as_string(self.config.name)
        if not self.pid:
            msg = ("attempted to send %s sig %s but it wasn't running" % (processname, signame(sig)))
            log.debug(msg)
            return msg

        log.debug('sending %s (pid %s) sig %s' % (processname, self.pid, signame(sig)))

        self._check_in_state(ProcessStates.RUNNING, ProcessStates.STARTING, ProcessStates.STOPPING)

        try:
            try:
                os.kill(self.pid, sig)
            except OSError as exc:
                if exc.errno == errno.ESRCH:
                    msg = ('unable to signal %s (pid %s), it probably just now exited '
                           'on its own: %s' % (processname, self.pid, str(exc)))
                    log.debug(msg)
                    # we could change the state here but we intentionally do not.  we will do it during normal SIGCHLD
                    # processing.
                    return None
                raise
        except:
            tb = traceback.format_exc()
            msg = 'unknown problem sending sig %s (%s):%s' % (processname, self.pid, tb)
            log.critical(msg)
            self.change_state(ProcessStates.UNKNOWN)
            return msg

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
                "not exit too quickly" % (processname, self.pid))

        exit_expected = es in self.config.exitcodes

        if self.killing:
            # likely the result of a stop request implies STOPPING -> STOPPED
            self.killing = False
            self.delay = 0
            self.exitstatus = es

            msg = 'stopped: %s (%s)' % (processname, msg)
            self._check_in_state(ProcessStates.STOPPING)
            self.change_state(ProcessStates.STOPPED)
            if exit_expected:
                log.info(msg)
            else:
                log.warning(msg)

        elif too_quickly:
            # the program did not stay up long enough to make it to RUNNING implies STARTING -> BACKOFF
            self.exitstatus = None
            self.spawn_err = 'Exited too quickly (process log may have details)'
            msg = 'exited: %s (%s)' % (processname, msg + '; not expected')
            self._check_in_state(ProcessStates.STARTING)
            self.change_state(ProcessStates.BACKOFF)
            log.warning(msg)

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
                msg = 'exited: %s (%s)' % (processname, msg + '; expected')
                self.change_state(ProcessStates.EXITED, expected=True)
                log.info(msg)
            else:
                # unexpected exit code
                self.spawn_err = 'Bad exit code %s' % es
                msg = 'exited: %s (%s)' % (processname, msg + '; not expected')
                self.change_state(ProcessStates.EXITED, expected=False)
                log.warning(msg)

        self.pid = 0
        close_parent_pipes(self._pipes)
        self._pipes = {}
        self._dispatchers = {}

        # if we died before we processed the current event (only happens if we're an event listener), notify the event
        # system that this event was rejected so it can be processed again.
        if self.event is not None:
            # Note: this should only be true if we were in the BUSY state when finish() was called.
            notify_event(EventRejectedEvent(self, self.event))
            self.event = None

    def set_uid(self) -> str | None:
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
        return '<Subprocess at %s with name %s in state %s>' % (
            id(self), name, get_process_state_description(self.get_state()))

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
                    elif self.exitstatus not in self.config.exitcodes:
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
                logger.info('success: %s %s' % (processname, msg))

        if state == ProcessStates.BACKOFF:
            if self.backoff > self.config.startretries:
                # BACKOFF -> FATAL if the proc has exceeded its number of retries
                self.give_up()
                msg = ('entered FATAL state, too many start retries too quickly')
                logger.info('gave up: %s %s' % (processname, msg))

        elif state == ProcessStates.STOPPING:
            time_left = self.delay - now
            if time_left <= 0:
                # kill processes which are taking too long to stop with a final sigkill.  if this doesn't kill it, the
                # process will be stuck in the STOPPING state forever.
                log.warning('killing \'%s\' (%s) with SIGKILL' % (processname, self.pid))
                self.kill(signal.SIGKILL)

    def create_auto_child_logs(self):
        # temporary logfiles which are erased at start time
        get_autoname = self.context.get_auto_child_log_name
        sid = self.context.config.identifier
        name = self.config.name
        # if self.stdout_logfile is Automatic:
        #     self.stdout_logfile = get_autoname(name, sid, 'stdout')
        # if self.stderr_logfile is Automatic:
        #     self.stderr_logfile = get_autoname(name, sid, 'stderr')


@functools.total_ordering
class ProcessGroup:
    def __init__(self, config: ProcessGroupConfig, context: ServerContext):
        self.config = config
        self.context = context
        self.processes = {}
        for pconfig in self.config.processes:
            process = Subprocess(pconfig, self, self.context)
            self.processes[pconfig.name] = process

    def __lt__(self, other):
        return self.config.priority < other.config.priority

    def __eq__(self, other):
        return self.config.priority == other.config.priority

    def __repr__(self):
        # repr can't return anything other than a native string, but the name might be unicode - a problem on Python 2.
        name = self.config.name
        return '<%s instance at %s named %s>' % (self.__class__, id(self), name)

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

    def get_unstopped_processes(self) -> list[Subprocess]:
        return [x for x in self.processes.values() if x.get_state() not in STOPPED_STATES]

    def get_dispatchers(self) -> dict[int, Dispatcher]:
        dispatchers = {}
        for process in self.processes.values():
            dispatchers.update(process._dispatchers)
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
# supervisord.py


log = logging.getLogger(__name__)


class Supervisor:
    stopping = False  # set after we detect that we are handling a stop request
    last_shutdown_report = 0  # throttle for delayed process error reports at stop
    process_groups = None  # map of process group name to process group object
    stop_groups = None  # list used for priority ordered shutdown

    def __init__(self, context: ServerContext) -> None:
        super().__init__()

        self.context = context
        self.process_groups = {}
        self.ticks = {}

    def main(self):
        if not self.context.first:
            # prevent crash on libdispatch-based systems, at least for the first request
            self.context.cleanup_fds()

        self.context.set_uid_or_exit()

        if self.context.first:
            self.context.set_rlimits_or_exit()

        # this sets the options.logger object delay logger instantiation until after setuid
        if not self.context.config.nocleanup:
            # clean up old automatic logs
            self.context.clear_auto_child_logdir()

        self.run()

    def run(self):
        self.process_groups = {}  # clear
        self.stop_groups = None  # clear
        clear_events()
        try:
            for config in self.context.config.groups:
                self.add_process_group(config)
            self.context.set_signals()
            if not self.context.config.nodaemon and self.context.first:
                self.context.daemonize()
            # writing pid file needs to come *after* daemonizing or pid will be wrong
            self.context.write_pidfile()
            self.runforever()
        finally:
            self.context.cleanup()

    def diff_to_active(self):
        new = self.context.config.groups
        cur = [group.config for group in self.process_groups.values()]

        curdict = dict(zip([cfg.name for cfg in cur], cur))
        newdict = dict(zip([cfg.name for cfg in new], new))

        added = [cand for cand in new if cand.name not in curdict]
        removed = [cand for cand in cur if cand.name not in newdict]

        changed = [cand for cand in new if cand != curdict.get(cand.name, cand)]

        return added, changed, removed

    def add_process_group(self, config):
        name = config.name
        if name not in self.process_groups:
            group = self.process_groups[name] = ProcessGroup(config, self.context)
            group.after_setuid()
            notify_event(ProcessGroupAddedEvent(name))
            return True
        return False

    def remove_process_group(self, name):
        if self.process_groups[name].get_unstopped_processes():
            return False
        self.process_groups[name].before_remove()
        del self.process_groups[name]
        notify_event(ProcessGroupRemovedEvent(name))
        return True

    def get_process_map(self):
        process_map = {}
        for group in self.process_groups.values():
            process_map.update(group.get_dispatchers())
        return process_map

    def shutdown_report(self):
        unstopped = []

        for group in self.process_groups.values():
            unstopped.extend(group.get_unstopped_processes())

        if unstopped:
            # throttle 'waiting for x to die' reports
            now = time.time()
            if now > (self.last_shutdown_report + 3):  # every 3 secs
                names = [as_string(p.config.name) for p in unstopped]
                namestr = ', '.join(names)
                log.info('waiting for %s to die' % namestr)
                self.last_shutdown_report = now
                for proc in unstopped:
                    state = get_process_state_description(proc.get_state())
                    log.debug(
                        '%s state: %s' % (proc.config.name, state))
        return unstopped

    def ordered_stop_groups_phase_1(self):
        if self.stop_groups:
            # stop the last group (the one with the "highest" priority)
            self.stop_groups[-1].stop_all()

    def ordered_stop_groups_phase_2(self):
        # after phase 1 we've transitioned and reaped, let's see if we can remove the group we stopped from the
        # stop_groups queue.
        if self.stop_groups:
            # pop the last group (the one with the "highest" priority)
            group = self.stop_groups.pop()
            if group.get_unstopped_processes():
                # if any processes in the group aren't yet in a stopped state, we're not yet done shutting this group
                # down, so push it back on to the end of the stop group queue
                self.stop_groups.append(group)

    def runforever(self):
        notify_event(SupervisorRunningEvent())
        timeout = 1  # this cannot be fewer than the smallest TickEvent (5)

        while 1:
            combined_map = {}
            combined_map.update(self.get_process_map())

            pgroups = list(self.process_groups.values())
            pgroups.sort()

            if self.context.state < SupervisorStates.RUNNING:
                if not self.stopping:
                    # first time, set the stopping flag, do a notification and set stop_groups
                    self.stopping = True
                    self.stop_groups = pgroups[:]
                    notify_event(SupervisorStoppingEvent())

                self.ordered_stop_groups_phase_1()

                if not self.shutdown_report():
                    # if there are no unstopped processes (we're done killing everything), it's OK to shutdown or reload
                    raise ExitNow

            for fd, dispatcher in combined_map.items():
                if dispatcher.readable():
                    self.context.poller.register_readable(fd)
                if dispatcher.writable():
                    self.context.poller.register_writable(fd)

            r, w = self.context.poller.poll(timeout)

            for fd in r:
                if fd in combined_map:
                    try:
                        dispatcher = combined_map[fd]
                        log.debug('read event caused by %(dispatcher)r', dispatcher=dispatcher)
                        dispatcher.handle_read_event()
                        if not dispatcher.readable():
                            self.context.poller.unregister_readable(fd)
                    except ExitNow:
                        raise
                    except:
                        combined_map[fd].handle_error()
                else:
                    # if the fd is not in combined_map, we should unregister it. otherwise, it will be polled every
                    # time, which may cause 100% cpu usage
                    log.debug('unexpected read event from fd %r' % fd)
                    try:
                        self.context.poller.unregister_readable(fd)
                    except:
                        pass

            for fd in w:
                if fd in combined_map:
                    try:
                        dispatcher = combined_map[fd]
                        log.debug('write event caused by %(dispatcher)r', dispatcher=dispatcher)
                        dispatcher.handle_write_event()
                        if not dispatcher.writable():
                            self.context.poller.unregister_writable(fd)
                    except ExitNow:
                        raise
                    except:
                        combined_map[fd].handle_error()
                else:
                    log.debug('unexpected write event from fd %r' % fd)
                    try:
                        self.context.poller.unregister_writable(fd)
                    except:
                        pass

            for group in pgroups:
                group.transition()

            self.reap()
            self.handle_signal()
            self.tick()

            if self.context.state < SupervisorStates.RUNNING:
                self.ordered_stop_groups_phase_2()

            if self.context.test:
                break

    def tick(self, now=None):
        """ Send one or more 'tick' events when the timeslice related to the period for the event type rolls over """
        if now is None:
            # now won't be None in unit tests
            now = time.time()
        for event in TICK_EVENTS:
            period = event.period
            last_tick = self.ticks.get(period)
            if last_tick is None:
                # we just started up
                last_tick = self.ticks[period] = timeslice(period, now)
            this_tick = timeslice(period, now)
            if this_tick != last_tick:
                self.ticks[period] = this_tick
                notify_event(event(this_tick, self))

    def reap(self, once=False, recursionguard=0):
        if recursionguard == 100:
            return
        pid, sts = self.context.waitpid()
        if pid:
            process = self.context.pid_history.get(pid, None)
            if process is None:
                _, msg = decode_wait_status(sts)
                log.info('reaped unknown pid %s (%s)' % (pid, msg))
            else:
                process.finish(sts)
                del self.context.pid_history[pid]
            if not once:
                # keep reaping until no more kids to reap, but don't recurse infinitely
                self.reap(once=False, recursionguard=recursionguard + 1)

    def handle_signal(self):
        sig = self.context.get_signal()
        if sig:
            if sig in (signal.SIGTERM, signal.SIGINT, signal.SIGQUIT):
                log.warning('received %s indicating exit request' % signame(sig))
                self.context.state = SupervisorStates.SHUTDOWN

            elif sig == signal.SIGHUP:
                if self.context.state == SupervisorStates.SHUTDOWN:
                    log.warning('ignored %s indicating restart request (shutdown in progress)' % signame(sig))  # noqa
                else:
                    log.warning('received %s indicating restart request' % signame(sig))  # noqa
                    self.context.state = SupervisorStates.RESTARTING

            elif sig == signal.SIGCHLD:
                log.debug('received %s indicating a child quit' % signame(sig))

            elif sig == signal.SIGUSR2:
                log.info('received %s indicating log reopen request' % signame(sig))
                # self.context.reopen_logs()
                for group in self.process_groups.values():
                    group.reopen_logs()

            else:
                log.debug('received %s indicating nothing' % signame(sig))

    def get_state(self):
        return self.context.state


def timeslice(period, when):
    return int(when - (when % period))


def main(args=None, test=False):
    setup_standard_logging('INFO')

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
