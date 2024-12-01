#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omlish-lite
# @omlish-script
# @omlish-amalg-output main.py
# ruff: noqa: N802 UP006 UP007 UP036
import abc
import base64
import contextlib
import dataclasses as dc
import datetime
import functools
import inspect
import json
import logging
import os
import platform
import pwd
import shlex
import site
import struct
import subprocess
import sys
import textwrap
import threading
import time
import typing as ta
import zlib


########################################


if sys.version_info < (3, 8):
    raise OSError(f'Requires python (3, 8), got {sys.version_info} from {sys.executable}')  # noqa


########################################


# commands/base.py
CommandInputT = ta.TypeVar('CommandInputT', bound='Command.Input')
CommandOutputT = ta.TypeVar('CommandOutputT', bound='Command.Output')

# ../../../omlish/lite/cached.py
T = ta.TypeVar('T')

# ../../../omlish/lite/check.py
SizedT = ta.TypeVar('SizedT', bound=ta.Sized)


########################################
# ../commands/base.py


##


class Command(abc.ABC, ta.Generic[CommandInputT, CommandOutputT]):
    @dc.dataclass(frozen=True)
    class Input(abc.ABC):  # noqa
        pass

    @dc.dataclass(frozen=True)
    class Output(abc.ABC):  # noqa
        pass

    @abc.abstractmethod
    def _execute(self, inp: CommandInputT) -> CommandOutputT:
        raise NotImplementedError


########################################
# ../../../pyremote.py
"""
Basically this: https://mitogen.networkgenomics.com/howitworks.html
"""


##


_PYREMOTE_BOOTSTRAP_COMM_FD = 100
_PYREMOTE_BOOTSTRAP_SRC_FD = 101

_PYREMOTE_BOOTSTRAP_CHILD_PID_VAR = '_OPYR_CPID'
_PYREMOTE_BOOTSTRAP_ARGV0_VAR = '_OPYR_ARGV0'

_PYREMOTE_BOOTSTRAP_ACK0 = b'OPYR000\n'
_PYREMOTE_BOOTSTRAP_ACK1 = b'OPYR001\n'
_PYREMOTE_BOOTSTRAP_ACK2 = b'OPYR002\n'
_PYREMOTE_BOOTSTRAP_ACK3 = b'OPYR003\n'

_PYREMOTE_BOOTSTRAP_PROC_TITLE_FMT = '(pyremote:%s)'

_PYREMOTE_BOOTSTRAP_IMPORTS = [
    'base64',
    'os',
    'struct',
    'sys',
    'zlib',
]


def _pyremote_bootstrap_main(context_name: str) -> None:
    # Get pid
    pid = os.getpid()

    # Two copies of main src to be sent to parent
    r0, w0 = os.pipe()
    r1, w1 = os.pipe()

    if (cp := os.fork()):
        # Parent process

        # Dup original stdin to comm_fd for use as comm channel
        os.dup2(0, _PYREMOTE_BOOTSTRAP_COMM_FD)

        # Overwrite stdin (fed to python repl) with first copy of src
        os.dup2(r0, 0)

        # Dup second copy of src to src_fd to recover after launch
        os.dup2(r1, _PYREMOTE_BOOTSTRAP_SRC_FD)

        # Close remaining fd's
        for f in [r0, w0, r1, w1]:
            os.close(f)

        # Save child pid to close after relaunch
        os.environ[_PYREMOTE_BOOTSTRAP_CHILD_PID_VAR] = str(cp)

        # Save original argv0
        os.environ[_PYREMOTE_BOOTSTRAP_ARGV0_VAR] = sys.executable

        # Start repl reading stdin from r0
        os.execl(sys.executable, sys.executable + (_PYREMOTE_BOOTSTRAP_PROC_TITLE_FMT % (context_name,)))

    else:
        # Child process

        # Write first ack
        os.write(1, _PYREMOTE_BOOTSTRAP_ACK0)

        # Write pid
        os.write(1, struct.pack('<Q', pid))

        # Read main src from stdin
        main_z_len = struct.unpack('<I', os.read(0, 4))[0]
        main_src = zlib.decompress(os.fdopen(0, 'rb').read(main_z_len))

        # Write both copies of main src. Must write to w0 (parent stdin) before w1 (copy pipe) as pipe will likely fill
        # and block and need to be drained by pyremote_bootstrap_finalize running in parent.
        for w in [w0, w1]:
            fp = os.fdopen(w, 'wb', 0)
            fp.write(main_src)
            fp.close()

        # Write second ack
        os.write(1, _PYREMOTE_BOOTSTRAP_ACK1)

        # Exit child
        sys.exit(0)


##


def pyremote_build_bootstrap_cmd(context_name: str) -> str:
    if any(c in context_name for c in '\'"'):
        raise NameError(context_name)

    bs_src = textwrap.dedent(inspect.getsource(_pyremote_bootstrap_main))

    for gl in [
        '_PYREMOTE_BOOTSTRAP_COMM_FD',
        '_PYREMOTE_BOOTSTRAP_SRC_FD',

        '_PYREMOTE_BOOTSTRAP_CHILD_PID_VAR',
        '_PYREMOTE_BOOTSTRAP_ARGV0_VAR',

        '_PYREMOTE_BOOTSTRAP_ACK0',
        '_PYREMOTE_BOOTSTRAP_ACK1',

        '_PYREMOTE_BOOTSTRAP_PROC_TITLE_FMT',
    ]:
        bs_src = bs_src.replace(gl, repr(globals()[gl]))

    bs_src = '\n'.join(
        cl
        for l in bs_src.splitlines()
        if (cl := (l.split('#')[0]).rstrip())
        if cl.strip()
    )

    bs_z = zlib.compress(bs_src.encode('utf-8'))
    bs_z64 = base64.encodebytes(bs_z).replace(b'\n', b'')

    def dq_repr(o: ta.Any) -> str:
        return '"' + repr(o)[1:-1] + '"'

    stmts = [
        f'import {", ".join(_PYREMOTE_BOOTSTRAP_IMPORTS)}',
        f'exec(zlib.decompress(base64.decodebytes({bs_z64!r})))',
        f'_pyremote_bootstrap_main({context_name!r})',
    ]

    cmd = '; '.join(stmts)
    return cmd


##


@dc.dataclass(frozen=True)
class PyremoteEnvInfo:
    sys_base_prefix: str
    sys_byteorder: str
    sys_defaultencoding: str
    sys_exec_prefix: str
    sys_executable: str
    sys_implementation_name: str
    sys_path: ta.List[str]
    sys_platform: str
    sys_prefix: str
    sys_version: str
    sys_version_info: ta.List[ta.Union[int, str]]

    platform_architecture: ta.List[str]
    platform_machine: str
    platform_platform: str
    platform_processor: str
    platform_system: str
    platform_release: str
    platform_version: str

    site_userbase: str

    os_cwd: str
    os_gid: int
    os_loadavg: ta.List[float]
    os_login: ta.Optional[str]
    os_pgrp: int
    os_pid: int
    os_ppid: int
    os_uid: int

    pw_name: str
    pw_uid: int
    pw_gid: int
    pw_gecos: str
    pw_dir: str
    pw_shell: str

    env_path: ta.Optional[str]


def _get_pyremote_env_info() -> PyremoteEnvInfo:
    os_uid = os.getuid()

    pw = pwd.getpwuid(os_uid)

    os_login: ta.Optional[str]
    try:
        os_login = os.getlogin()
    except OSError:
        os_login = None

    return PyremoteEnvInfo(
        sys_base_prefix=sys.base_prefix,
        sys_byteorder=sys.byteorder,
        sys_defaultencoding=sys.getdefaultencoding(),
        sys_exec_prefix=sys.exec_prefix,
        sys_executable=sys.executable,
        sys_implementation_name=sys.implementation.name,
        sys_path=sys.path,
        sys_platform=sys.platform,
        sys_prefix=sys.prefix,
        sys_version=sys.version,
        sys_version_info=list(sys.version_info),

        platform_architecture=list(platform.architecture()),
        platform_machine=platform.machine(),
        platform_platform=platform.platform(),
        platform_processor=platform.processor(),
        platform_system=platform.system(),
        platform_release=platform.release(),
        platform_version=platform.version(),

        site_userbase=site.getuserbase(),

        os_cwd=os.getcwd(),
        os_gid=os.getgid(),
        os_loadavg=list(os.getloadavg()),
        os_login=os_login,
        os_pgrp=os.getpgrp(),
        os_pid=os.getpid(),
        os_ppid=os.getppid(),
        os_uid=os_uid,

        pw_name=pw.pw_name,
        pw_uid=pw.pw_uid,
        pw_gid=pw.pw_gid,
        pw_gecos=pw.pw_gecos,
        pw_dir=pw.pw_dir,
        pw_shell=pw.pw_shell,

        env_path=os.environ.get('PATH'),
    )


##


class PyremoteBootstrapDriver:
    def __init__(self, main_src: str) -> None:
        super().__init__()

        self._main_src = main_src
        self._main_z = zlib.compress(main_src.encode('utf-8'))

    #

    @dc.dataclass(frozen=True)
    class Read:
        sz: int

    @dc.dataclass(frozen=True)
    class Write:
        d: bytes

    class ProtocolError(Exception):
        pass

    @dc.dataclass(frozen=True)
    class Result:
        pid: int
        env_info: PyremoteEnvInfo

    def gen(self) -> ta.Generator[ta.Union[Read, Write], ta.Optional[bytes], Result]:
        # Read first ack
        yield from self._expect(_PYREMOTE_BOOTSTRAP_ACK0)

        # Read pid
        d = yield from self._read(8)
        pid = struct.unpack('<Q', d)[0]

        # Write main src
        yield from self._write(struct.pack('<I', len(self._main_z)))
        yield from self._write(self._main_z)

        # Read second and third ack
        yield from self._expect(_PYREMOTE_BOOTSTRAP_ACK1)
        yield from self._expect(_PYREMOTE_BOOTSTRAP_ACK2)

        # Read env info
        d = yield from self._read(4)
        env_info_json_len = struct.unpack('<I', d)[0]
        d = yield from self._read(env_info_json_len)
        env_info_json = d.decode('utf-8')
        env_info = PyremoteEnvInfo(**json.loads(env_info_json))

        # Read fourth ack
        yield from self._expect(_PYREMOTE_BOOTSTRAP_ACK3)

        # Return
        return self.Result(
            pid=pid,
            env_info=env_info,
        )

    def _read(self, sz: int) -> ta.Generator[Read, bytes, bytes]:
        d = yield self.Read(sz)
        if not isinstance(d, bytes):
            raise self.ProtocolError(f'Expected bytes after read, got {d!r}')
        if len(d) != sz:
            raise self.ProtocolError(f'Read {len(d)} bytes, expected {sz}')
        return d

    def _expect(self, e: bytes) -> ta.Generator[Read, bytes, None]:
        d = yield from self._read(len(e))
        if d != e:
            raise self.ProtocolError(f'Read {d!r}, expected {e!r}')

    def _write(self, d: bytes) -> ta.Generator[Write, ta.Optional[bytes], None]:
        i = yield self.Write(d)
        if i is not None:
            raise self.ProtocolError('Unexpected input after write')

    #

    def run(self, stdin: ta.IO, stdout: ta.IO) -> Result:
        gen = self.gen()

        gi: ta.Optional[bytes] = None
        while True:
            try:
                if gi is not None:
                    go = gen.send(gi)
                else:
                    go = next(gen)
            except StopIteration as e:
                return e.value

            if isinstance(go, self.Read):
                gi = stdout.read(go.sz)
            elif isinstance(go, self.Write):
                gi = None
                stdin.write(go.d)
                stdin.flush()
            else:
                raise TypeError(go)


##


@dc.dataclass(frozen=True)
class PyremotePayloadRuntime:
    input: ta.BinaryIO
    main_src: str
    env_info: PyremoteEnvInfo


def pyremote_bootstrap_finalize() -> PyremotePayloadRuntime:
    # Restore original argv0
    sys.executable = os.environ.pop(_PYREMOTE_BOOTSTRAP_ARGV0_VAR)

    # Read second copy of main src
    r1 = os.fdopen(_PYREMOTE_BOOTSTRAP_SRC_FD, 'rb', 0)
    main_src = r1.read().decode('utf-8')
    r1.close()

    # Reap boostrap child. Must be done after reading second copy of source because source may be too big to fit in a
    # pipe at once.
    os.waitpid(int(os.environ.pop(_PYREMOTE_BOOTSTRAP_CHILD_PID_VAR)), 0)

    # Write third ack
    os.write(1, _PYREMOTE_BOOTSTRAP_ACK2)

    # Write env info
    env_info = _get_pyremote_env_info()
    env_info_json = json.dumps(dc.asdict(env_info), indent=None, separators=(',', ':'))  # noqa
    os.write(1, struct.pack('<I', len(env_info_json)))
    os.write(1, env_info_json.encode('utf-8'))

    # Write fourth ack
    os.write(1, _PYREMOTE_BOOTSTRAP_ACK3)

    # Return
    return PyremotePayloadRuntime(
        input=os.fdopen(_PYREMOTE_BOOTSTRAP_COMM_FD, 'rb', 0),
        main_src=main_src,
        env_info=env_info,
    )


########################################
# ../../../../omlish/lite/cached.py


class _cached_nullary:  # noqa
    def __init__(self, fn):
        super().__init__()
        self._fn = fn
        self._value = self._missing = object()
        functools.update_wrapper(self, fn)

    def __call__(self, *args, **kwargs):  # noqa
        if self._value is self._missing:
            self._value = self._fn()
        return self._value

    def __get__(self, instance, owner):  # noqa
        bound = instance.__dict__[self._fn.__name__] = self.__class__(self._fn.__get__(instance, owner))
        return bound


def cached_nullary(fn):  # ta.Callable[..., T]) -> ta.Callable[..., T]:
    return _cached_nullary(fn)


########################################
# ../../../../omlish/lite/check.py


def check_isinstance(v: ta.Any, spec: ta.Union[ta.Type[T], tuple]) -> T:
    if not isinstance(v, spec):
        raise TypeError(v)
    return v


def check_not_isinstance(v: T, spec: ta.Union[type, tuple]) -> T:
    if isinstance(v, spec):
        raise TypeError(v)
    return v


def check_none(v: T) -> None:
    if v is not None:
        raise ValueError(v)


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


def check_is(l: T, r: T) -> T:
    if l is not r:
        raise ValueError(l, r)
    return l


def check_is_not(l: T, r: ta.Any) -> T:
    if l is r:
        raise ValueError(l, r)
    return l


def check_in(v: T, c: ta.Container[T]) -> T:
    if v not in c:
        raise ValueError(v, c)
    return v


def check_not_in(v: T, c: ta.Container[T]) -> T:
    if v in c:
        raise ValueError(v, c)
    return v


def check_single(vs: ta.Iterable[T]) -> T:
    [v] = vs
    return v


def check_empty(v: SizedT) -> SizedT:
    if len(v):
        raise ValueError(v)
    return v


def check_non_empty(v: SizedT) -> SizedT:
    if not len(v):
        raise ValueError(v)
    return v


########################################
# ../../../../omlish/lite/json.py


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
# ../../../../omlish/lite/logs.py
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
            t = ct.strftime('%Y-%m-%d %H:%M:%S')
            return '%s.%03d' % (t, record.msecs)  # noqa


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
        handler_factory: ta.Optional[ta.Callable[[], logging.Handler]] = None,
) -> ta.Optional[StandardLogHandler]:
    with _locking_logging_module_lock():
        if target is None:
            target = logging.root

        #

        if not force:
            if any(isinstance(h, StandardLogHandler) for h in list(target.handlers)):
                return None

        #

        if handler_factory is not None:
            handler = handler_factory()
        else:
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
# ../../../../omlish/lite/runtime.py


@cached_nullary
def is_debugger_attached() -> bool:
    return any(frame[1].endswith('pydevd.py') for frame in inspect.stack())


REQUIRED_PYTHON_VERSION = (3, 8)


def check_runtime_version() -> None:
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        raise OSError(f'Requires python {REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa


########################################
# ../../../../omlish/lite/subprocesses.py


##


_SUBPROCESS_SHELL_WRAP_EXECS = False


def subprocess_shell_wrap_exec(*args: str) -> ta.Tuple[str, ...]:
    return ('sh', '-c', ' '.join(map(shlex.quote, args)))


def subprocess_maybe_shell_wrap_exec(*args: str) -> ta.Tuple[str, ...]:
    if _SUBPROCESS_SHELL_WRAP_EXECS or is_debugger_attached():
        return subprocess_shell_wrap_exec(*args)
    else:
        return args


def _prepare_subprocess_invocation(
        *args: str,
        env: ta.Optional[ta.Mapping[str, ta.Any]] = None,
        extra_env: ta.Optional[ta.Mapping[str, ta.Any]] = None,
        quiet: bool = False,
        shell: bool = False,
        **kwargs: ta.Any,
) -> ta.Tuple[ta.Tuple[ta.Any, ...], ta.Dict[str, ta.Any]]:
    log.debug(args)
    if extra_env:
        log.debug(extra_env)

    if extra_env:
        env = {**(env if env is not None else os.environ), **extra_env}

    if quiet and 'stderr' not in kwargs:
        if not log.isEnabledFor(logging.DEBUG):
            kwargs['stderr'] = subprocess.DEVNULL

    if not shell:
        args = subprocess_maybe_shell_wrap_exec(*args)

    return args, dict(
        env=env,
        shell=shell,
        **kwargs,
    )


def subprocess_check_call(*args: str, stdout=sys.stderr, **kwargs: ta.Any) -> None:
    args, kwargs = _prepare_subprocess_invocation(*args, stdout=stdout, **kwargs)
    return subprocess.check_call(args, **kwargs)  # type: ignore


def subprocess_check_output(*args: str, **kwargs: ta.Any) -> bytes:
    args, kwargs = _prepare_subprocess_invocation(*args, **kwargs)
    return subprocess.check_output(args, **kwargs)


def subprocess_check_output_str(*args: str, **kwargs: ta.Any) -> str:
    return subprocess_check_output(*args, **kwargs).decode().strip()


##


DEFAULT_SUBPROCESS_TRY_EXCEPTIONS: ta.Tuple[ta.Type[Exception], ...] = (
    FileNotFoundError,
    subprocess.CalledProcessError,
)


def subprocess_try_call(
        *args: str,
        try_exceptions: ta.Tuple[ta.Type[Exception], ...] = DEFAULT_SUBPROCESS_TRY_EXCEPTIONS,
        **kwargs: ta.Any,
) -> bool:
    try:
        subprocess_check_call(*args, **kwargs)
    except try_exceptions as e:  # noqa
        if log.isEnabledFor(logging.DEBUG):
            log.exception('command failed')
        return False
    else:
        return True


def subprocess_try_output(
        *args: str,
        try_exceptions: ta.Tuple[ta.Type[Exception], ...] = DEFAULT_SUBPROCESS_TRY_EXCEPTIONS,
        **kwargs: ta.Any,
) -> ta.Optional[bytes]:
    try:
        return subprocess_check_output(*args, **kwargs)
    except try_exceptions as e:  # noqa
        if log.isEnabledFor(logging.DEBUG):
            log.exception('command failed')
        return None


def subprocess_try_output_str(*args: str, **kwargs: ta.Any) -> ta.Optional[str]:
    out = subprocess_try_output(*args, **kwargs)
    return out.decode().strip() if out is not None else None


##


def subprocess_close(
        proc: subprocess.Popen,
        timeout: ta.Optional[float] = None,
) -> None:
    # TODO: terminate, sleep, kill
    if proc.stdout:
        proc.stdout.close()
    if proc.stderr:
        proc.stderr.close()
    if proc.stdin:
        proc.stdin.close()

    proc.wait(timeout)


########################################
# ../commands/subprocess.py


##


class SubprocessCommand(Command['SubprocessCommand.Input', 'SubprocessCommand.Output']):
    @dc.dataclass(frozen=True)
    class Input(Command.Input):
        args: ta.Sequence[str]

        shell: bool = False
        cwd: ta.Optional[str] = None
        env: ta.Optional[ta.Mapping[str, str]] = None

        capture_stdout: bool = False
        capture_stderr: bool = False

        input: ta.Optional[bytes] = None
        timeout: ta.Optional[float] = None

        def __post_init__(self) -> None:
            if isinstance(self.args, str):
                raise TypeError(self.args)

    @dc.dataclass(frozen=True)
    class Output(Command.Output):
        rc: int
        pid: int

        elapsed_s: float

        stdout: ta.Optional[bytes] = None
        stderr: ta.Optional[bytes] = None

    def _execute(self, inp: Input) -> Output:
        proc = subprocess.Popen(
            subprocess_maybe_shell_wrap_exec(*inp.args),

            shell=inp.shell,
            cwd=inp.cwd,
            env={**os.environ, **(inp.env or {})},

            stdin=subprocess.PIPE if inp.input is not None else None,
            stdout=subprocess.PIPE if inp.capture_stdout else None,
            stderr=subprocess.PIPE if inp.capture_stderr else None,
        )

        start_time = time.time()
        stdout, stderr = proc.communicate(
            input=inp.input,
            timeout=inp.timeout,
        )
        end_time = time.time()

        return SubprocessCommand.Output(
            rc=proc.returncode,
            pid=proc.pid,

            elapsed_s=end_time - start_time,

            stdout=stdout,  # noqa
            stderr=stderr,  # noqa
        )


########################################
# main.py


##


def _run_a_command() -> None:
    i = SubprocessCommand.Input(
        args=['python3', '-'],
        input=b'print(1)\n',
        capture_stdout=True,
    )

    o = SubprocessCommand()._execute(i)  # noqa
    print(o)


def _remote_main() -> None:
    rt = pyremote_bootstrap_finalize()  # noqa

    _run_a_command()


def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--ssh')
    parser.add_argument('--python', default='python3')
    parser.add_argument('--_amalg-file')

    args = parser.parse_args()

    #

    self_src = inspect.getsource(sys.modules[__name__])
    self_src_lines = self_src.splitlines()
    for l in self_src_lines:
        if l.startswith('# @omlish-amalg-output '):
            is_self_amalg = True
            break
    else:
        is_self_amalg = False

    if is_self_amalg:
        amalg_src = self_src
    else:
        amalg_file = args._amalg_file  # noqa
        if amalg_file is None:
            amalg_file = os.path.join(os.path.dirname(__file__), '_manage.py')
        with open(amalg_file) as f:
            amalg_src = f.read()

    #

    remote_src = '\n\n'.join([
        '__name__ = "__remote__"',
        amalg_src,
        '_remote_main()',
    ])

    #

    bs_src = pyremote_build_bootstrap_cmd(__package__ or 'manage')

    if args.ssh is not None:
        sh_src = ' '.join([args.python, '-c', shlex.quote(bs_src)])
        sh_cmd = f'{args.ssh} {shlex.quote(sh_src)}'
        cmd = [sh_cmd]
        shell = True
    else:
        cmd = [args.python, '-c', bs_src]
        shell = False

    proc = subprocess.Popen(
        subprocess_maybe_shell_wrap_exec(*cmd),
        shell=shell,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    stdin = check_not_none(proc.stdin)
    stdout = check_not_none(proc.stdout)

    res = PyremoteBootstrapDriver(remote_src).run(stdin, stdout)
    print(res)

    print(stdout.read())
    proc.wait()


if __name__ == '__main__':
    _main()
