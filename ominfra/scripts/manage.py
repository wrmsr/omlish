#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omlish-lite
# @omlish-script
# @omlish-amalg-output ../manage/main.py
# ruff: noqa: N802 UP006 UP007 UP036
"""
manage.py -s 'docker run -i python:3.12'
manage.py -s 'ssh -i /foo/bar.pem foo@bar.baz' -q --python=python3.8
"""
import abc
import base64
import collections.abc
import contextlib
import dataclasses as dc
import datetime
import decimal
import enum
import fractions
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
import threading
import time
import traceback
import types
import typing as ta
import uuid
import weakref  # noqa
import zlib


########################################


if sys.version_info < (3, 8):
    raise OSError(f'Requires python (3, 8), got {sys.version_info} from {sys.executable}')  # noqa


########################################


# ../../omlish/lite/cached.py
T = ta.TypeVar('T')
CallableT = ta.TypeVar('CallableT', bound=ta.Callable)

# ../../omlish/lite/check.py
SizedT = ta.TypeVar('SizedT', bound=ta.Sized)

# commands/base.py
CommandT = ta.TypeVar('CommandT', bound='Command')
CommandOutputT = ta.TypeVar('CommandOutputT', bound='Command.Output')

# ../../omlish/lite/inject.py
U = ta.TypeVar('U')
InjectorKeyCls = ta.Union[type, ta.NewType]
InjectorProviderFn = ta.Callable[['Injector'], ta.Any]
InjectorProviderFnMap = ta.Mapping['InjectorKey', 'InjectorProviderFn']
InjectorBindingOrBindings = ta.Union['InjectorBinding', 'InjectorBindings']

# ../../omlish/lite/subprocesses.py
SubprocessChannelOption = ta.Literal['pipe', 'stdout', 'devnull']


########################################
# ../config.py


@dc.dataclass(frozen=True)
class MainConfig:
    log_level: ta.Optional[str] = 'INFO'

    debug: bool = False


########################################
# ../../pyremote.py
"""
Basically this: https://mitogen.networkgenomics.com/howitworks.html

TODO:
 - log: ta.Optional[logging.Logger] = None + log.debug's
"""


##


@dc.dataclass(frozen=True)
class PyremoteBootstrapOptions:
    debug: bool = False

    DEFAULT_MAIN_NAME_OVERRIDE: ta.ClassVar[str] = '__pyremote__'
    main_name_override: ta.Optional[str] = DEFAULT_MAIN_NAME_OVERRIDE


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


_PYREMOTE_BOOTSTRAP_INPUT_FD = 100
_PYREMOTE_BOOTSTRAP_SRC_FD = 101

_PYREMOTE_BOOTSTRAP_CHILD_PID_VAR = '_OPYR_CHILD_PID'
_PYREMOTE_BOOTSTRAP_ARGV0_VAR = '_OPYR_ARGV0'
_PYREMOTE_BOOTSTRAP_CONTEXT_NAME_VAR = '_OPYR_CONTEXT_NAME'
_PYREMOTE_BOOTSTRAP_SRC_FILE_VAR = '_OPYR_SRC_FILE'
_PYREMOTE_BOOTSTRAP_OPTIONS_JSON_VAR = '_OPYR_OPTIONS_JSON'

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
        os.dup2(0, _PYREMOTE_BOOTSTRAP_INPUT_FD)

        # Overwrite stdin (fed to python repl) with first copy of src
        os.dup2(r0, 0)

        # Dup second copy of src to src_fd to recover after launch
        os.dup2(r1, _PYREMOTE_BOOTSTRAP_SRC_FD)

        # Close remaining fd's
        for f in [r0, w0, r1, w1]:
            os.close(f)

        # Save vars
        env = os.environ
        exe = sys.executable
        env[_PYREMOTE_BOOTSTRAP_CHILD_PID_VAR] = str(cp)
        env[_PYREMOTE_BOOTSTRAP_ARGV0_VAR] = exe
        env[_PYREMOTE_BOOTSTRAP_CONTEXT_NAME_VAR] = context_name

        # Start repl reading stdin from r0
        os.execl(exe, exe + (_PYREMOTE_BOOTSTRAP_PROC_TITLE_FMT % (context_name,)))

    else:
        # Child process

        # Write first ack
        os.write(1, _PYREMOTE_BOOTSTRAP_ACK0)

        # Write pid
        os.write(1, struct.pack('<Q', pid))

        # Read main src from stdin
        main_z_len = struct.unpack('<I', os.read(0, 4))[0]
        if len(main_z := os.fdopen(0, 'rb').read(main_z_len)) != main_z_len:
            raise EOFError
        main_src = zlib.decompress(main_z)

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

    import inspect
    import textwrap
    bs_src = textwrap.dedent(inspect.getsource(_pyremote_bootstrap_main))

    for gl in [
        '_PYREMOTE_BOOTSTRAP_INPUT_FD',
        '_PYREMOTE_BOOTSTRAP_SRC_FD',

        '_PYREMOTE_BOOTSTRAP_CHILD_PID_VAR',
        '_PYREMOTE_BOOTSTRAP_ARGV0_VAR',
        '_PYREMOTE_BOOTSTRAP_CONTEXT_NAME_VAR',

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

    bs_z = zlib.compress(bs_src.encode('utf-8'), 9)
    bs_z85 = base64.b85encode(bs_z).replace(b'\n', b'')

    stmts = [
        f'import {", ".join(_PYREMOTE_BOOTSTRAP_IMPORTS)}',
        f'exec(zlib.decompress(base64.b85decode({bs_z85!r})))',
        f'_pyremote_bootstrap_main({context_name!r})',
    ]

    cmd = '; '.join(stmts)
    return cmd


##


@dc.dataclass(frozen=True)
class PyremotePayloadRuntime:
    input: ta.BinaryIO
    output: ta.BinaryIO
    context_name: str
    main_src: str
    options: PyremoteBootstrapOptions
    env_info: PyremoteEnvInfo


def pyremote_bootstrap_finalize() -> PyremotePayloadRuntime:
    # If src file var is not present we need to do initial finalization
    if _PYREMOTE_BOOTSTRAP_SRC_FILE_VAR not in os.environ:
        # Read second copy of main src
        r1 = os.fdopen(_PYREMOTE_BOOTSTRAP_SRC_FD, 'rb', 0)
        main_src = r1.read().decode('utf-8')
        r1.close()

        # Reap boostrap child. Must be done after reading second copy of source because source may be too big to fit in
        # a pipe at once.
        os.waitpid(int(os.environ.pop(_PYREMOTE_BOOTSTRAP_CHILD_PID_VAR)), 0)

        # Read options
        options_json_len = struct.unpack('<I', os.read(_PYREMOTE_BOOTSTRAP_INPUT_FD, 4))[0]
        if len(options_json := os.read(_PYREMOTE_BOOTSTRAP_INPUT_FD, options_json_len)) != options_json_len:
            raise EOFError
        options = PyremoteBootstrapOptions(**json.loads(options_json.decode('utf-8')))

        # If debugging, re-exec as file
        if options.debug:
            # Write temp source file
            import tempfile
            tfd, tfn = tempfile.mkstemp('-pyremote.py')
            os.write(tfd, main_src.encode('utf-8'))
            os.close(tfd)

            # Set vars
            os.environ[_PYREMOTE_BOOTSTRAP_SRC_FILE_VAR] = tfn
            os.environ[_PYREMOTE_BOOTSTRAP_OPTIONS_JSON_VAR] = options_json.decode('utf-8')

            # Re-exec temp file
            exe = os.environ[_PYREMOTE_BOOTSTRAP_ARGV0_VAR]
            context_name = os.environ[_PYREMOTE_BOOTSTRAP_CONTEXT_NAME_VAR]
            os.execl(exe, exe + (_PYREMOTE_BOOTSTRAP_PROC_TITLE_FMT % (context_name,)), tfn)

    else:
        # Load options json var
        options_json_str = os.environ.pop(_PYREMOTE_BOOTSTRAP_OPTIONS_JSON_VAR)
        options = PyremoteBootstrapOptions(**json.loads(options_json_str))

        # Read temp source file
        with open(os.environ.pop(_PYREMOTE_BOOTSTRAP_SRC_FILE_VAR)) as sf:
            main_src = sf.read()

    # Restore original argv0
    sys.executable = os.environ.pop(_PYREMOTE_BOOTSTRAP_ARGV0_VAR)

    # Grab context name
    context_name = os.environ.pop(_PYREMOTE_BOOTSTRAP_CONTEXT_NAME_VAR)

    # Write third ack
    os.write(1, _PYREMOTE_BOOTSTRAP_ACK2)

    # Write env info
    env_info = _get_pyremote_env_info()
    env_info_json = json.dumps(dc.asdict(env_info), indent=None, separators=(',', ':'))  # noqa
    os.write(1, struct.pack('<I', len(env_info_json)))
    os.write(1, env_info_json.encode('utf-8'))

    # Setup IO
    input = os.fdopen(_PYREMOTE_BOOTSTRAP_INPUT_FD, 'rb', 0)  # noqa
    output = os.fdopen(os.dup(1), 'wb', 0)  # noqa
    os.dup2(nfd := os.open('/dev/null', os.O_WRONLY), 1)
    os.close(nfd)

    if (mn := options.main_name_override) is not None:
        # Inspections like typing.get_type_hints need an entry in sys.modules.
        sys.modules[mn] = sys.modules['__main__']

    # Write fourth ack
    output.write(_PYREMOTE_BOOTSTRAP_ACK3)

    # Return
    return PyremotePayloadRuntime(
        input=input,
        output=output,
        context_name=context_name,
        main_src=main_src,
        options=options,
        env_info=env_info,
    )


##


class PyremoteBootstrapDriver:
    def __init__(
            self,
            main_src: ta.Union[str, ta.Sequence[str]],
            options: PyremoteBootstrapOptions = PyremoteBootstrapOptions(),
    ) -> None:
        super().__init__()

        self._main_src = main_src
        self._options = options

        self._prepared_main_src = self._prepare_main_src(main_src, options)
        self._main_z = zlib.compress(self._prepared_main_src.encode('utf-8'))

        self._options_json = json.dumps(dc.asdict(options), indent=None, separators=(',', ':')).encode('utf-8')  # noqa
    #

    @classmethod
    def _prepare_main_src(
            cls,
            main_src: ta.Union[str, ta.Sequence[str]],
            options: PyremoteBootstrapOptions,
    ) -> str:
        parts: ta.List[str]
        if isinstance(main_src, str):
            parts = [main_src]
        else:
            parts = list(main_src)

        if (mn := options.main_name_override) is not None:
            parts.insert(0, f'__name__ = {mn!r}')

        if len(parts) == 1:
            return parts[0]
        else:
            return '\n\n'.join(parts)

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
        # Read first ack (after fork)
        yield from self._expect(_PYREMOTE_BOOTSTRAP_ACK0)

        # Read pid
        d = yield from self._read(8)
        pid = struct.unpack('<Q', d)[0]

        # Write main src
        yield from self._write(struct.pack('<I', len(self._main_z)))
        yield from self._write(self._main_z)

        # Read second ack (after writing src copies)
        yield from self._expect(_PYREMOTE_BOOTSTRAP_ACK1)

        # Write options
        yield from self._write(struct.pack('<I', len(self._options_json)))
        yield from self._write(self._options_json)

        # Read third ack (after reaping child process)
        yield from self._expect(_PYREMOTE_BOOTSTRAP_ACK2)

        # Read env info
        d = yield from self._read(4)
        env_info_json_len = struct.unpack('<I', d)[0]
        d = yield from self._read(env_info_json_len)
        env_info_json = d.decode('utf-8')
        env_info = PyremoteEnvInfo(**json.loads(env_info_json))

        # Read fourth ack (after finalization completed)
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

    def run(self, input: ta.IO, output: ta.IO) -> Result:  # noqa
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
                if len(gi := input.read(go.sz)) != go.sz:
                    raise EOFError
            elif isinstance(go, self.Write):
                gi = None
                output.write(go.d)
                output.flush()
            else:
                raise TypeError(go)


########################################
# ../../../omlish/lite/cached.py


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


def static_init(fn: CallableT) -> CallableT:
    fn = cached_nullary(fn)
    fn()
    return fn


########################################
# ../../../omlish/lite/check.py


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
# ../../../omlish/lite/maybes.py


class Maybe(ta.Generic[T]):
    @property
    @abc.abstractmethod
    def present(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def must(self) -> T:
        raise NotImplementedError

    @classmethod
    def just(cls, v: T) -> 'Maybe[T]':
        return tuple.__new__(_Maybe, (v,))  # noqa

    _empty: ta.ClassVar['Maybe']

    @classmethod
    def empty(cls) -> 'Maybe[T]':
        return Maybe._empty


class _Maybe(Maybe[T], tuple):
    __slots__ = ()

    def __init_subclass__(cls, **kwargs):
        raise TypeError

    @property
    def present(self) -> bool:
        return bool(self)

    def must(self) -> T:
        if not self:
            raise ValueError
        return self[0]


Maybe._empty = tuple.__new__(_Maybe, ())  # noqa


########################################
# ../../../omlish/lite/pycharm.py


DEFAULT_PYCHARM_VERSION = '242.23726.102'


@dc.dataclass(frozen=True)
class PycharmRemoteDebug:
    port: int
    host: ta.Optional[str] = 'localhost'
    install_version: ta.Optional[str] = DEFAULT_PYCHARM_VERSION


def pycharm_debug_connect(prd: PycharmRemoteDebug) -> None:
    if prd.install_version is not None:
        import subprocess
        import sys
        subprocess.check_call([
            sys.executable,
            '-mpip',
            'install',
            f'pydevd-pycharm~={prd.install_version}',
        ])

    pydevd_pycharm = __import__('pydevd_pycharm')  # noqa
    pydevd_pycharm.settrace(
        prd.host,
        port=prd.port,
        stdoutToServer=True,
        stderrToServer=True,
    )


def pycharm_debug_preamble(prd: PycharmRemoteDebug) -> str:
    import inspect
    import textwrap

    return textwrap.dedent(f"""
        {inspect.getsource(pycharm_debug_connect)}

        pycharm_debug_connect(PycharmRemoteDebug(
            {prd.port!r},
            host={prd.host!r},
            install_version={prd.install_version!r},
        ))
    """)


########################################
# ../../../omlish/lite/reflect.py


_GENERIC_ALIAS_TYPES = (
    ta._GenericAlias,  # type: ignore  # noqa
    *([ta._SpecialGenericAlias] if hasattr(ta, '_SpecialGenericAlias') else []),  # noqa
)


def is_generic_alias(obj, *, origin: ta.Any = None) -> bool:
    return (
        isinstance(obj, _GENERIC_ALIAS_TYPES) and
        (origin is None or ta.get_origin(obj) is origin)
    )


is_union_alias = functools.partial(is_generic_alias, origin=ta.Union)
is_callable_alias = functools.partial(is_generic_alias, origin=ta.Callable)


def is_optional_alias(spec: ta.Any) -> bool:
    return (
        isinstance(spec, _GENERIC_ALIAS_TYPES) and  # noqa
        ta.get_origin(spec) is ta.Union and
        len(ta.get_args(spec)) == 2 and
        any(a in (None, type(None)) for a in ta.get_args(spec))
    )


def get_optional_alias_arg(spec: ta.Any) -> ta.Any:
    [it] = [it for it in ta.get_args(spec) if it not in (None, type(None))]
    return it


def is_new_type(spec: ta.Any) -> bool:
    if isinstance(ta.NewType, type):
        return isinstance(spec, ta.NewType)
    else:
        # Before https://github.com/python/cpython/commit/c2f33dfc83ab270412bf243fb21f724037effa1a
        return isinstance(spec, types.FunctionType) and spec.__code__ is ta.NewType.__code__.co_consts[1]  # type: ignore  # noqa


def deep_subclasses(cls: ta.Type[T]) -> ta.Iterator[ta.Type[T]]:
    seen = set()
    todo = list(reversed(cls.__subclasses__()))
    while todo:
        cur = todo.pop()
        if cur in seen:
            continue
        seen.add(cur)
        yield cur
        todo.extend(reversed(cur.__subclasses__()))


########################################
# ../../../omlish/lite/strings.py


##


def camel_case(name: str, lower: bool = False) -> str:
    if not name:
        return ''
    s = ''.join(map(str.capitalize, name.split('_')))  # noqa
    if lower:
        s = s[0].lower() + s[1:]
    return s


def snake_case(name: str) -> str:
    uppers: list[int | None] = [i for i, c in enumerate(name) if c.isupper()]
    return '_'.join([name[l:r].lower() for l, r in zip([None, *uppers], [*uppers, None])]).strip('_')


##


def is_dunder(name: str) -> bool:
    return (
        name[:2] == name[-2:] == '__' and
        name[2:3] != '_' and
        name[-3:-2] != '_' and
        len(name) > 4
    )


def is_sunder(name: str) -> bool:
    return (
        name[0] == name[-1] == '_' and
        name[1:2] != '_' and
        name[-2:-1] != '_' and
        len(name) > 2
    )


##


def attr_repr(obj: ta.Any, *attrs: str) -> str:
    return f'{type(obj).__name__}({", ".join(f"{attr}={getattr(obj, attr)!r}" for attr in attrs)})'


##


FORMAT_NUM_BYTES_SUFFIXES: ta.Sequence[str] = ['B', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB']


def format_num_bytes(num_bytes: int) -> str:
    for i, suffix in enumerate(FORMAT_NUM_BYTES_SUFFIXES):
        value = num_bytes / 1024 ** i
        if num_bytes < 1024 ** (i + 1):
            if value.is_integer():
                return f'{int(value)}{suffix}'
            else:
                return f'{value:.2f}{suffix}'

    return f'{num_bytes / 1024 ** (len(FORMAT_NUM_BYTES_SUFFIXES) - 1):.2f}{FORMAT_NUM_BYTES_SUFFIXES[-1]}'


########################################
# ../commands/base.py


##


@dc.dataclass(frozen=True)
class Command(abc.ABC, ta.Generic[CommandOutputT]):
    @dc.dataclass(frozen=True)
    class Output(abc.ABC):  # noqa
        pass

    @ta.final
    def execute(self, executor: 'CommandExecutor') -> CommandOutputT:
        return check_isinstance(executor.execute(self), self.Output)  # type: ignore[return-value]


##


@dc.dataclass(frozen=True)
class CommandException:
    name: str
    repr: str

    traceback: ta.Optional[str] = None

    exc: ta.Optional[ta.Any] = None  # Exception

    cmd: ta.Optional[Command] = None

    @classmethod
    def of(
            cls,
            exc: Exception,
            *,
            omit_exc_object: bool = False,

            cmd: ta.Optional[Command] = None,
    ) -> 'CommandException':
        return CommandException(
            name=type(exc).__qualname__,
            repr=repr(exc),

            traceback=(
                ''.join(traceback.format_tb(exc.__traceback__))
                if getattr(exc, '__traceback__', None) is not None else None
            ),

            exc=None if omit_exc_object else exc,

            cmd=cmd,
        )


class CommandOutputOrException(abc.ABC, ta.Generic[CommandOutputT]):
    @property
    @abc.abstractmethod
    def output(self) -> ta.Optional[CommandOutputT]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def exception(self) -> ta.Optional[CommandException]:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class CommandOutputOrExceptionData(CommandOutputOrException):
    output: ta.Optional[Command.Output] = None
    exception: ta.Optional[CommandException] = None


class CommandExecutor(abc.ABC, ta.Generic[CommandT, CommandOutputT]):
    @abc.abstractmethod
    def execute(self, cmd: CommandT) -> CommandOutputT:
        raise NotImplementedError

    def try_execute(
            self,
            cmd: CommandT,
            *,
            log: ta.Optional[logging.Logger] = None,
            omit_exc_object: bool = False,
    ) -> CommandOutputOrException[CommandOutputT]:
        try:
            o = self.execute(cmd)

        except Exception as e:  # noqa
            if log is not None:
                log.exception('Exception executing command: %r', type(cmd))

            return CommandOutputOrExceptionData(exception=CommandException.of(
                e,
                omit_exc_object=omit_exc_object,
                cmd=cmd,
            ))

        else:
            return CommandOutputOrExceptionData(output=o)


##


@dc.dataclass(frozen=True)
class CommandRegistration:
    command_cls: ta.Type[Command]

    name: ta.Optional[str] = None

    @property
    def name_or_default(self) -> str:
        if not (cls_name := self.command_cls.__name__).endswith('Command'):
            raise NameError(cls_name)
        return snake_case(cls_name[:-len('Command')])


CommandRegistrations = ta.NewType('CommandRegistrations', ta.Sequence[CommandRegistration])


##


@dc.dataclass(frozen=True)
class CommandExecutorRegistration:
    command_cls: ta.Type[Command]
    executor_cls: ta.Type[CommandExecutor]


CommandExecutorRegistrations = ta.NewType('CommandExecutorRegistrations', ta.Sequence[CommandExecutorRegistration])


##


CommandNameMap = ta.NewType('CommandNameMap', ta.Mapping[str, ta.Type[Command]])


def build_command_name_map(crs: CommandRegistrations) -> CommandNameMap:
    dct: ta.Dict[str, ta.Type[Command]] = {}
    cr: CommandRegistration
    for cr in crs:
        if (name := cr.name_or_default) in dct:
            raise NameError(name)
        dct[name] = cr.command_cls
    return CommandNameMap(dct)


########################################
# ../remote/config.py


@dc.dataclass(frozen=True)
class RemoteConfig:
    payload_file: ta.Optional[str] = None

    pycharm_remote_debug: ta.Optional[PycharmRemoteDebug] = None


########################################
# ../remote/payload.py


RemoteExecutionPayloadFile = ta.NewType('RemoteExecutionPayloadFile', str)


@cached_nullary
def _get_self_src() -> str:
    return inspect.getsource(sys.modules[__name__])


def _is_src_amalg(src: str) -> bool:
    for l in src.splitlines():  # noqa
        if l.startswith('# @omlish-amalg-output '):
            return True
    return False


@cached_nullary
def _is_self_amalg() -> bool:
    return _is_src_amalg(_get_self_src())


def get_remote_payload_src(
        *,
        file: ta.Optional[RemoteExecutionPayloadFile],
) -> str:
    if file is not None:
        with open(file) as f:
            return f.read()

    if _is_self_amalg():
        return _get_self_src()

    import importlib.resources
    return importlib.resources.files(__package__.split('.')[0] + '.scripts').joinpath('manage.py').read_text()


########################################
# ../../../omlish/lite/inject.py


###
# types


@dc.dataclass(frozen=True)
class InjectorKey(ta.Generic[T]):
    # Before PEP-560 typing.Generic was a metaclass with a __new__ that takes a 'cls' arg, so instantiating a dataclass
    # with kwargs (such as through dc.replace) causes `TypeError: __new__() got multiple values for argument 'cls'`.
    # See:
    #  - https://github.com/python/cpython/commit/d911e40e788fb679723d78b6ea11cabf46caed5a
    #  - https://gist.github.com/wrmsr/4468b86efe9f373b6b114bfe85b98fd3
    cls_: InjectorKeyCls

    tag: ta.Any = None
    array: bool = False


def is_valid_injector_key_cls(cls: ta.Any) -> bool:
    return isinstance(cls, type) or is_new_type(cls)


def check_valid_injector_key_cls(cls: T) -> T:
    if not is_valid_injector_key_cls(cls):
        raise TypeError(cls)
    return cls


##


class InjectorProvider(abc.ABC):
    @abc.abstractmethod
    def provider_fn(self) -> InjectorProviderFn:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class InjectorBinding:
    key: InjectorKey
    provider: InjectorProvider


class InjectorBindings(abc.ABC):
    @abc.abstractmethod
    def bindings(self) -> ta.Iterator[InjectorBinding]:
        raise NotImplementedError

##


class Injector(abc.ABC):
    @abc.abstractmethod
    def try_provide(self, key: ta.Any) -> Maybe[ta.Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def provide(self, key: ta.Any) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def provide_kwargs(
            self,
            obj: ta.Any,
            *,
            skip_args: int = 0,
            skip_kwargs: ta.Optional[ta.Iterable[ta.Any]] = None,
    ) -> ta.Mapping[str, ta.Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def inject(
            self,
            obj: ta.Any,
            *,
            args: ta.Optional[ta.Sequence[ta.Any]] = None,
            kwargs: ta.Optional[ta.Mapping[str, ta.Any]] = None,
    ) -> ta.Any:
        raise NotImplementedError

    def __getitem__(
            self,
            target: ta.Union[InjectorKey[T], ta.Type[T]],
    ) -> T:
        return self.provide(target)


###
# exceptions


class InjectorError(Exception):
    pass


@dc.dataclass()
class InjectorKeyError(InjectorError):
    key: InjectorKey

    source: ta.Any = None
    name: ta.Optional[str] = None


class UnboundInjectorKeyError(InjectorKeyError):
    pass


class DuplicateInjectorKeyError(InjectorKeyError):
    pass


class CyclicDependencyInjectorKeyError(InjectorKeyError):
    pass


###
# keys


def as_injector_key(o: ta.Any) -> InjectorKey:
    if o is inspect.Parameter.empty:
        raise TypeError(o)
    if isinstance(o, InjectorKey):
        return o
    if is_valid_injector_key_cls(o):
        return InjectorKey(o)
    raise TypeError(o)


###
# providers


@dc.dataclass(frozen=True)
class FnInjectorProvider(InjectorProvider):
    fn: ta.Any

    def __post_init__(self) -> None:
        check_not_isinstance(self.fn, type)

    def provider_fn(self) -> InjectorProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.inject(self.fn)

        return pfn


@dc.dataclass(frozen=True)
class CtorInjectorProvider(InjectorProvider):
    cls_: type

    def __post_init__(self) -> None:
        check_isinstance(self.cls_, type)

    def provider_fn(self) -> InjectorProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.inject(self.cls_)

        return pfn


@dc.dataclass(frozen=True)
class ConstInjectorProvider(InjectorProvider):
    v: ta.Any

    def provider_fn(self) -> InjectorProviderFn:
        return lambda _: self.v


@dc.dataclass(frozen=True)
class SingletonInjectorProvider(InjectorProvider):
    p: InjectorProvider

    def __post_init__(self) -> None:
        check_isinstance(self.p, InjectorProvider)

    def provider_fn(self) -> InjectorProviderFn:
        v = not_set = object()

        def pfn(i: Injector) -> ta.Any:
            nonlocal v
            if v is not_set:
                v = ufn(i)
            return v

        ufn = self.p.provider_fn()
        return pfn


@dc.dataclass(frozen=True)
class LinkInjectorProvider(InjectorProvider):
    k: InjectorKey

    def __post_init__(self) -> None:
        check_isinstance(self.k, InjectorKey)

    def provider_fn(self) -> InjectorProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.provide(self.k)

        return pfn


@dc.dataclass(frozen=True)
class ArrayInjectorProvider(InjectorProvider):
    ps: ta.Sequence[InjectorProvider]

    def provider_fn(self) -> InjectorProviderFn:
        ps = [p.provider_fn() for p in self.ps]

        def pfn(i: Injector) -> ta.Any:
            rv = []
            for ep in ps:
                o = ep(i)
                rv.append(o)
            return rv

        return pfn


###
# bindings


@dc.dataclass(frozen=True)
class _InjectorBindings(InjectorBindings):
    bs: ta.Optional[ta.Sequence[InjectorBinding]] = None
    ps: ta.Optional[ta.Sequence[InjectorBindings]] = None

    def bindings(self) -> ta.Iterator[InjectorBinding]:
        if self.bs is not None:
            yield from self.bs
        if self.ps is not None:
            for p in self.ps:
                yield from p.bindings()


def as_injector_bindings(*args: InjectorBindingOrBindings) -> InjectorBindings:
    bs: ta.List[InjectorBinding] = []
    ps: ta.List[InjectorBindings] = []

    for a in args:
        if isinstance(a, InjectorBindings):
            ps.append(a)
        elif isinstance(a, InjectorBinding):
            bs.append(a)
        else:
            raise TypeError(a)

    return _InjectorBindings(
        bs or None,
        ps or None,
    )


##


@dc.dataclass(frozen=True)
class OverridesInjectorBindings(InjectorBindings):
    p: InjectorBindings
    m: ta.Mapping[InjectorKey, InjectorBinding]

    def bindings(self) -> ta.Iterator[InjectorBinding]:
        for b in self.p.bindings():
            yield self.m.get(b.key, b)


def injector_override(p: InjectorBindings, *args: InjectorBindingOrBindings) -> InjectorBindings:
    m: ta.Dict[InjectorKey, InjectorBinding] = {}

    for b in as_injector_bindings(*args).bindings():
        if b.key in m:
            raise DuplicateInjectorKeyError(b.key)
        m[b.key] = b

    return OverridesInjectorBindings(p, m)


##


def build_injector_provider_map(bs: InjectorBindings) -> ta.Mapping[InjectorKey, InjectorProvider]:
    pm: ta.Dict[InjectorKey, InjectorProvider] = {}
    am: ta.Dict[InjectorKey, ta.List[InjectorProvider]] = {}

    for b in bs.bindings():
        if b.key.array:
            al = am.setdefault(b.key, [])
            if isinstance(b.provider, ArrayInjectorProvider):
                al.extend(b.provider.ps)
            else:
                al.append(b.provider)
        else:
            if b.key in pm:
                raise KeyError(b.key)
            pm[b.key] = b.provider

    if am:
        for k, aps in am.items():
            pm[k] = ArrayInjectorProvider(aps)

    return pm


###
# inspection


class _InjectionInspection(ta.NamedTuple):
    signature: inspect.Signature
    type_hints: ta.Mapping[str, ta.Any]
    args_offset: int


_INJECTION_INSPECTION_CACHE: ta.MutableMapping[ta.Any, _InjectionInspection] = weakref.WeakKeyDictionary()


def _do_injection_inspect(obj: ta.Any) -> _InjectionInspection:
    tgt = obj
    if isinstance(tgt, type) and tgt.__init__ is not object.__init__:  # type: ignore[misc]
        # Python 3.8's inspect.signature can't handle subclasses overriding __new__, always generating *args/**kwargs.
        #  - https://bugs.python.org/issue40897
        #  - https://github.com/python/cpython/commit/df7c62980d15acd3125dfbd81546dad359f7add7
        tgt = tgt.__init__  # type: ignore[misc]
        has_generic_base = True
    else:
        has_generic_base = False

    # inspect.signature(eval_str=True) was added in 3.10 and we have to support 3.8, so we have to get_type_hints to
    # eval str annotations *in addition to* getting the signature for parameter information.
    uw = tgt
    has_partial = False
    while True:
        if isinstance(uw, functools.partial):
            has_partial = True
            uw = uw.func
        else:
            if (uw2 := inspect.unwrap(uw)) is uw:
                break
            uw = uw2

    if has_generic_base and has_partial:
        raise InjectorError(
            'Injector inspection does not currently support both a typing.Generic base and a functools.partial: '
            f'{obj}',
        )

    return _InjectionInspection(
        inspect.signature(tgt),
        ta.get_type_hints(uw),
        1 if has_generic_base else 0,
    )


def _injection_inspect(obj: ta.Any) -> _InjectionInspection:
    try:
        return _INJECTION_INSPECTION_CACHE[obj]
    except TypeError:
        return _do_injection_inspect(obj)
    except KeyError:
        pass
    insp = _do_injection_inspect(obj)
    _INJECTION_INSPECTION_CACHE[obj] = insp
    return insp


class InjectionKwarg(ta.NamedTuple):
    name: str
    key: InjectorKey
    has_default: bool


class InjectionKwargsTarget(ta.NamedTuple):
    obj: ta.Any
    kwargs: ta.Sequence[InjectionKwarg]


def build_injection_kwargs_target(
        obj: ta.Any,
        *,
        skip_args: int = 0,
        skip_kwargs: ta.Optional[ta.Iterable[str]] = None,
        raw_optional: bool = False,
) -> InjectionKwargsTarget:
    insp = _injection_inspect(obj)

    params = list(insp.signature.parameters.values())

    skip_names: ta.Set[str] = set()
    if skip_kwargs is not None:
        skip_names.update(check_not_isinstance(skip_kwargs, str))

    seen: ta.Set[InjectorKey] = set()
    kws: ta.List[InjectionKwarg] = []
    for p in params[insp.args_offset + skip_args:]:
        if p.name in skip_names:
            continue

        if p.annotation is inspect.Signature.empty:
            if p.default is not inspect.Parameter.empty:
                raise KeyError(f'{obj}, {p.name}')
            continue

        if p.kind not in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY):
            raise TypeError(insp)

        # 3.8 inspect.signature doesn't eval_str but typing.get_type_hints does, so prefer that.
        ann = insp.type_hints.get(p.name, p.annotation)
        if (
                not raw_optional and
                is_optional_alias(ann)
        ):
            ann = get_optional_alias_arg(ann)

        k = as_injector_key(ann)

        if k in seen:
            raise DuplicateInjectorKeyError(k)
        seen.add(k)

        kws.append(InjectionKwarg(
            p.name,
            k,
            p.default is not inspect.Parameter.empty,
        ))

    return InjectionKwargsTarget(
        obj,
        kws,
    )


###
# injector


_INJECTOR_INJECTOR_KEY: InjectorKey[Injector] = InjectorKey(Injector)


@dc.dataclass(frozen=True)
class _InjectorEager:
    key: InjectorKey


_INJECTOR_EAGER_ARRAY_KEY: InjectorKey[_InjectorEager] = InjectorKey(_InjectorEager, array=True)


class _Injector(Injector):
    def __init__(self, bs: InjectorBindings, p: ta.Optional[Injector] = None) -> None:
        super().__init__()

        self._bs = check_isinstance(bs, InjectorBindings)
        self._p: ta.Optional[Injector] = check_isinstance(p, (Injector, type(None)))

        self._pfm = {k: v.provider_fn() for k, v in build_injector_provider_map(bs).items()}

        if _INJECTOR_INJECTOR_KEY in self._pfm:
            raise DuplicateInjectorKeyError(_INJECTOR_INJECTOR_KEY)

        self.__cur_req: ta.Optional[_Injector._Request] = None

        if _INJECTOR_EAGER_ARRAY_KEY in self._pfm:
            for e in self.provide(_INJECTOR_EAGER_ARRAY_KEY):
                self.provide(e.key)

    class _Request:
        def __init__(self, injector: '_Injector') -> None:
            super().__init__()
            self._injector = injector
            self._provisions: ta.Dict[InjectorKey, Maybe] = {}
            self._seen_keys: ta.Set[InjectorKey] = set()

        def handle_key(self, key: InjectorKey) -> Maybe[Maybe]:
            try:
                return Maybe.just(self._provisions[key])
            except KeyError:
                pass
            if key in self._seen_keys:
                raise CyclicDependencyInjectorKeyError(key)
            self._seen_keys.add(key)
            return Maybe.empty()

        def handle_provision(self, key: InjectorKey, mv: Maybe) -> Maybe:
            check_in(key, self._seen_keys)
            check_not_in(key, self._provisions)
            self._provisions[key] = mv
            return mv

    @contextlib.contextmanager
    def _current_request(self) -> ta.Generator[_Request, None, None]:
        if (cr := self.__cur_req) is not None:
            yield cr
            return

        cr = self._Request(self)
        try:
            self.__cur_req = cr
            yield cr
        finally:
            self.__cur_req = None

    def try_provide(self, key: ta.Any) -> Maybe[ta.Any]:
        key = as_injector_key(key)

        cr: _Injector._Request
        with self._current_request() as cr:
            if (rv := cr.handle_key(key)).present:
                return rv.must()

            if key == _INJECTOR_INJECTOR_KEY:
                return cr.handle_provision(key, Maybe.just(self))

            fn = self._pfm.get(key)
            if fn is not None:
                return cr.handle_provision(key, Maybe.just(fn(self)))

            if self._p is not None:
                pv = self._p.try_provide(key)
                if pv is not None:
                    return cr.handle_provision(key, Maybe.empty())

            return cr.handle_provision(key, Maybe.empty())

    def provide(self, key: ta.Any) -> ta.Any:
        v = self.try_provide(key)
        if v.present:
            return v.must()
        raise UnboundInjectorKeyError(key)

    def provide_kwargs(
            self,
            obj: ta.Any,
            *,
            skip_args: int = 0,
            skip_kwargs: ta.Optional[ta.Iterable[ta.Any]] = None,
    ) -> ta.Mapping[str, ta.Any]:
        kt = build_injection_kwargs_target(
            obj,
            skip_args=skip_args,
            skip_kwargs=skip_kwargs,
        )

        ret: ta.Dict[str, ta.Any] = {}
        for kw in kt.kwargs:
            if kw.has_default:
                if not (mv := self.try_provide(kw.key)).present:
                    continue
                v = mv.must()
            else:
                v = self.provide(kw.key)
            ret[kw.name] = v
        return ret

    def inject(
            self,
            obj: ta.Any,
            *,
            args: ta.Optional[ta.Sequence[ta.Any]] = None,
            kwargs: ta.Optional[ta.Mapping[str, ta.Any]] = None,
    ) -> ta.Any:
        provided = self.provide_kwargs(
            obj,
            skip_args=len(args) if args is not None else 0,
            skip_kwargs=kwargs if kwargs is not None else None,
        )

        return obj(
            *(args if args is not None else ()),
            **(kwargs if kwargs is not None else {}),
            **provided,
        )


###
# binder


class InjectorBinder:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    _FN_TYPES: ta.Tuple[type, ...] = (
        types.FunctionType,
        types.MethodType,

        classmethod,
        staticmethod,

        functools.partial,
        functools.partialmethod,
    )

    @classmethod
    def _is_fn(cls, obj: ta.Any) -> bool:
        return isinstance(obj, cls._FN_TYPES)

    @classmethod
    def bind_as_fn(cls, icls: ta.Type[T]) -> ta.Type[T]:
        check_isinstance(icls, type)
        if icls not in cls._FN_TYPES:
            cls._FN_TYPES = (*cls._FN_TYPES, icls)
        return icls

    _BANNED_BIND_TYPES: ta.Tuple[type, ...] = (
        InjectorProvider,
    )

    @classmethod
    def bind(
            cls,
            obj: ta.Any,
            *,
            key: ta.Any = None,
            tag: ta.Any = None,
            array: ta.Optional[bool] = None,  # noqa

            to_fn: ta.Any = None,
            to_ctor: ta.Any = None,
            to_const: ta.Any = None,
            to_key: ta.Any = None,

            singleton: bool = False,

            eager: bool = False,
    ) -> InjectorBindingOrBindings:
        if obj is None or obj is inspect.Parameter.empty:
            raise TypeError(obj)
        if isinstance(obj, cls._BANNED_BIND_TYPES):
            raise TypeError(obj)

        ##

        if key is not None:
            key = as_injector_key(key)

        ##

        has_to = (
            to_fn is not None or
            to_ctor is not None or
            to_const is not None or
            to_key is not None
        )
        if isinstance(obj, InjectorKey):
            if key is None:
                key = obj
        elif isinstance(obj, type):
            if not has_to:
                to_ctor = obj
            if key is None:
                key = InjectorKey(obj)
        elif cls._is_fn(obj) and not has_to:
            to_fn = obj
            if key is None:
                insp = _injection_inspect(obj)
                key_cls: ta.Any = check_valid_injector_key_cls(check_not_none(insp.type_hints.get('return')))
                key = InjectorKey(key_cls)
        else:
            if to_const is not None:
                raise TypeError('Cannot bind instance with to_const')
            to_const = obj
            if key is None:
                key = InjectorKey(type(obj))
        del has_to

        ##

        if tag is not None:
            if key.tag is not None:
                raise TypeError('Tag already set')
            key = dc.replace(key, tag=tag)

        if array is not None:
            key = dc.replace(key, array=array)

        ##

        providers: ta.List[InjectorProvider] = []
        if to_fn is not None:
            providers.append(FnInjectorProvider(to_fn))
        if to_ctor is not None:
            providers.append(CtorInjectorProvider(to_ctor))
        if to_const is not None:
            providers.append(ConstInjectorProvider(to_const))
        if to_key is not None:
            providers.append(LinkInjectorProvider(as_injector_key(to_key)))
        if not providers:
            raise TypeError('Must specify provider')
        if len(providers) > 1:
            raise TypeError('May not specify multiple providers')
        provider, = providers

        ##

        if singleton:
            provider = SingletonInjectorProvider(provider)

        binding = InjectorBinding(key, provider)

        ##

        extras: ta.List[InjectorBinding] = []

        if eager:
            extras.append(bind_injector_eager_key(key))

        ##

        if extras:
            return as_injector_bindings(binding, *extras)
        else:
            return binding


###
# injection helpers


def make_injector_factory(
        fn: ta.Callable[..., T],
        cls: U,
        ann: ta.Any = None,
) -> ta.Callable[..., U]:
    if ann is None:
        ann = cls

    def outer(injector: Injector) -> ann:
        def inner(*args, **kwargs):
            return injector.inject(fn, args=args, kwargs=kwargs)
        return cls(inner)  # type: ignore

    return outer


def bind_injector_array(
        obj: ta.Any = None,
        *,
        tag: ta.Any = None,
) -> InjectorBindingOrBindings:
    key = as_injector_key(obj)
    if tag is not None:
        if key.tag is not None:
            raise ValueError('Must not specify multiple tags')
        key = dc.replace(key, tag=tag)

    if key.array:
        raise ValueError('Key must not be array')

    return InjectorBinding(
        dc.replace(key, array=True),
        ArrayInjectorProvider([]),
    )


def make_injector_array_type(
        ele: ta.Union[InjectorKey, InjectorKeyCls],
        cls: U,
        ann: ta.Any = None,
) -> ta.Callable[..., U]:
    if isinstance(ele, InjectorKey):
        if not ele.array:
            raise InjectorError('Provided key must be array', ele)
        key = ele
    else:
        key = dc.replace(as_injector_key(ele), array=True)

    if ann is None:
        ann = cls

    def inner(injector: Injector) -> ann:
        return cls(injector.provide(key))  # type: ignore[operator]

    return inner


def bind_injector_eager_key(key: ta.Any) -> InjectorBinding:
    return InjectorBinding(_INJECTOR_EAGER_ARRAY_KEY, ConstInjectorProvider(_InjectorEager(as_injector_key(key))))


##


class Injection:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    # keys

    @classmethod
    def as_key(cls, o: ta.Any) -> InjectorKey:
        return as_injector_key(o)

    @classmethod
    def array(cls, o: ta.Any) -> InjectorKey:
        return dc.replace(as_injector_key(o), array=True)

    @classmethod
    def tag(cls, o: ta.Any, t: ta.Any) -> InjectorKey:
        return dc.replace(as_injector_key(o), tag=t)

    # bindings

    @classmethod
    def as_bindings(cls, *args: InjectorBindingOrBindings) -> InjectorBindings:
        return as_injector_bindings(*args)

    @classmethod
    def override(cls, p: InjectorBindings, *args: InjectorBindingOrBindings) -> InjectorBindings:
        return injector_override(p, *args)

    # injector

    @classmethod
    def create_injector(cls, *args: InjectorBindingOrBindings, parent: ta.Optional[Injector] = None) -> Injector:
        return _Injector(as_injector_bindings(*args), parent)

    # binder

    @classmethod
    def bind(
            cls,
            obj: ta.Any,
            *,
            key: ta.Any = None,
            tag: ta.Any = None,
            array: ta.Optional[bool] = None,  # noqa

            to_fn: ta.Any = None,
            to_ctor: ta.Any = None,
            to_const: ta.Any = None,
            to_key: ta.Any = None,

            singleton: bool = False,

            eager: bool = False,
    ) -> InjectorBindingOrBindings:
        return InjectorBinder.bind(
            obj,

            key=key,
            tag=tag,
            array=array,

            to_fn=to_fn,
            to_ctor=to_ctor,
            to_const=to_const,
            to_key=to_key,

            singleton=singleton,

            eager=eager,
        )

    # helpers

    @classmethod
    def bind_factory(
            cls,
            fn: ta.Callable[..., T],
            cls_: U,
            ann: ta.Any = None,
    ) -> InjectorBindingOrBindings:
        return cls.bind(make_injector_factory(fn, cls_, ann))

    @classmethod
    def bind_array(
            cls,
            obj: ta.Any = None,
            *,
            tag: ta.Any = None,
    ) -> InjectorBindingOrBindings:
        return bind_injector_array(obj, tag=tag)

    @classmethod
    def bind_array_type(
            cls,
            ele: ta.Union[InjectorKey, InjectorKeyCls],
            cls_: U,
            ann: ta.Any = None,
    ) -> InjectorBindingOrBindings:
        return cls.bind(make_injector_array_type(ele, cls_, ann))


inj = Injection


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
# ../../../omlish/lite/marshal.py
"""
TODO:
 - pickle stdlib objs? have to pin to 3.8 pickle protocol, will be cross-version
 - nonstrict toggle
"""


##


@dc.dataclass(frozen=True)
class ObjMarshalOptions:
    pass


class ObjMarshaler(abc.ABC):
    @abc.abstractmethod
    def marshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def unmarshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        raise NotImplementedError


class NopObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return o

    def unmarshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return o


@dc.dataclass()
class ProxyObjMarshaler(ObjMarshaler):
    m: ta.Optional[ObjMarshaler] = None

    def marshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return check_not_none(self.m).marshal(o, opts)

    def unmarshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return check_not_none(self.m).unmarshal(o, opts)


@dc.dataclass(frozen=True)
class CastObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return o

    def unmarshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return self.ty(o)


class DynamicObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return marshal_obj(o)

    def unmarshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return o


@dc.dataclass(frozen=True)
class Base64ObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return base64.b64encode(o).decode('ascii')

    def unmarshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return self.ty(base64.b64decode(o))


@dc.dataclass(frozen=True)
class EnumObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return o.name

    def unmarshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return self.ty.__members__[o]  # type: ignore


@dc.dataclass(frozen=True)
class OptionalObjMarshaler(ObjMarshaler):
    item: ObjMarshaler

    def marshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        if o is None:
            return None
        return self.item.marshal(o, opts)

    def unmarshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        if o is None:
            return None
        return self.item.unmarshal(o, opts)


@dc.dataclass(frozen=True)
class MappingObjMarshaler(ObjMarshaler):
    ty: type
    km: ObjMarshaler
    vm: ObjMarshaler

    def marshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return {self.km.marshal(k, opts): self.vm.marshal(v, opts) for k, v in o.items()}

    def unmarshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return self.ty((self.km.unmarshal(k, opts), self.vm.unmarshal(v, opts)) for k, v in o.items())


@dc.dataclass(frozen=True)
class IterableObjMarshaler(ObjMarshaler):
    ty: type
    item: ObjMarshaler

    def marshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return [self.item.marshal(e, opts) for e in o]

    def unmarshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return self.ty(self.item.unmarshal(e, opts) for e in o)


@dc.dataclass(frozen=True)
class DataclassObjMarshaler(ObjMarshaler):
    ty: type
    fs: ta.Mapping[str, ObjMarshaler]
    nonstrict: bool = False

    def marshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return {k: m.marshal(getattr(o, k), opts) for k, m in self.fs.items()}

    def unmarshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return self.ty(**{k: self.fs[k].unmarshal(v, opts) for k, v in o.items() if not self.nonstrict or k in self.fs})


@dc.dataclass(frozen=True)
class PolymorphicObjMarshaler(ObjMarshaler):
    class Impl(ta.NamedTuple):
        ty: type
        tag: str
        m: ObjMarshaler

    impls_by_ty: ta.Mapping[type, Impl]
    impls_by_tag: ta.Mapping[str, Impl]

    @classmethod
    def of(cls, impls: ta.Iterable[Impl]) -> 'PolymorphicObjMarshaler':
        return cls(
            {i.ty: i for i in impls},
            {i.tag: i for i in impls},
        )

    def marshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        impl = self.impls_by_ty[type(o)]
        return {impl.tag: impl.m.marshal(o, opts)}

    def unmarshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        [(t, v)] = o.items()
        impl = self.impls_by_tag[t]
        return impl.m.unmarshal(v, opts)


@dc.dataclass(frozen=True)
class DatetimeObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return o.isoformat()

    def unmarshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return self.ty.fromisoformat(o)  # type: ignore


class DecimalObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return str(check_isinstance(o, decimal.Decimal))

    def unmarshal(self, v: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return decimal.Decimal(check_isinstance(v, str))


class FractionObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        fr = check_isinstance(o, fractions.Fraction)
        return [fr.numerator, fr.denominator]

    def unmarshal(self, v: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        num, denom = check_isinstance(v, list)
        return fractions.Fraction(num, denom)


class UuidObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return str(o)

    def unmarshal(self, o: ta.Any, opts: ObjMarshalOptions) -> ta.Any:
        return uuid.UUID(o)


##


_DEFAULT_OBJ_MARSHALERS: ta.Dict[ta.Any, ObjMarshaler] = {
    **{t: NopObjMarshaler() for t in (type(None),)},
    **{t: CastObjMarshaler(t) for t in (int, float, str, bool)},
    **{t: Base64ObjMarshaler(t) for t in (bytes, bytearray)},
    **{t: IterableObjMarshaler(t, DynamicObjMarshaler()) for t in (list, tuple, set, frozenset)},
    **{t: MappingObjMarshaler(t, DynamicObjMarshaler(), DynamicObjMarshaler()) for t in (dict,)},

    ta.Any: DynamicObjMarshaler(),

    **{t: DatetimeObjMarshaler(t) for t in (datetime.date, datetime.time, datetime.datetime)},
    decimal.Decimal: DecimalObjMarshaler(),
    fractions.Fraction: FractionObjMarshaler(),
    uuid.UUID: UuidObjMarshaler(),
}

_OBJ_MARSHALER_GENERIC_MAPPING_TYPES: ta.Dict[ta.Any, type] = {
    **{t: t for t in (dict,)},
    **{t: dict for t in (collections.abc.Mapping, collections.abc.MutableMapping)},
}

_OBJ_MARSHALER_GENERIC_ITERABLE_TYPES: ta.Dict[ta.Any, type] = {
    **{t: t for t in (list, tuple, set, frozenset)},
    collections.abc.Set: frozenset,
    collections.abc.MutableSet: set,
    collections.abc.Sequence: tuple,
    collections.abc.MutableSequence: list,
}


##


class ObjMarshalerManager:
    def __init__(
            self,
            *,
            default_options: ObjMarshalOptions = ObjMarshalOptions(),

            default_obj_marshalers: ta.Dict[ta.Any, ObjMarshaler] = _DEFAULT_OBJ_MARSHALERS,  # noqa
            generic_mapping_types: ta.Dict[ta.Any, type] = _OBJ_MARSHALER_GENERIC_MAPPING_TYPES,  # noqa
            generic_iterable_types: ta.Dict[ta.Any, type] = _OBJ_MARSHALER_GENERIC_ITERABLE_TYPES,  # noqa
    ) -> None:
        super().__init__()

        self._default_options = default_options

        self._obj_marshalers = dict(default_obj_marshalers)
        self._generic_mapping_types = generic_mapping_types
        self._generic_iterable_types = generic_iterable_types

        self._lock = threading.RLock()
        self._marshalers: ta.Dict[ta.Any, ObjMarshaler] = dict(_DEFAULT_OBJ_MARSHALERS)
        self._proxies: ta.Dict[ta.Any, ProxyObjMarshaler] = {}

    #

    def make_obj_marshaler(
            self,
            ty: ta.Any,
            rec: ta.Callable[[ta.Any], ObjMarshaler],
            *,
            nonstrict_dataclasses: bool = False,
    ) -> ObjMarshaler:
        if isinstance(ty, type):
            if abc.ABC in ty.__bases__:
                return PolymorphicObjMarshaler.of([  # type: ignore
                    PolymorphicObjMarshaler.Impl(
                        ity,
                        ity.__qualname__,
                        rec(ity),
                    )
                    for ity in deep_subclasses(ty)
                    if abc.ABC not in ity.__bases__
                ])

            if issubclass(ty, enum.Enum):
                return EnumObjMarshaler(ty)

            if dc.is_dataclass(ty):
                return DataclassObjMarshaler(
                    ty,
                    {f.name: rec(f.type) for f in dc.fields(ty)},
                    nonstrict=nonstrict_dataclasses,
                )

        if is_generic_alias(ty):
            try:
                mt = self._generic_mapping_types[ta.get_origin(ty)]
            except KeyError:
                pass
            else:
                k, v = ta.get_args(ty)
                return MappingObjMarshaler(mt, rec(k), rec(v))

            try:
                st = self._generic_iterable_types[ta.get_origin(ty)]
            except KeyError:
                pass
            else:
                [e] = ta.get_args(ty)
                return IterableObjMarshaler(st, rec(e))

            if is_union_alias(ty):
                return OptionalObjMarshaler(rec(get_optional_alias_arg(ty)))

        raise TypeError(ty)

    #

    def register_opj_marshaler(self, ty: ta.Any, m: ObjMarshaler) -> None:
        with self._lock:
            if ty in self._obj_marshalers:
                raise KeyError(ty)
            self._obj_marshalers[ty] = m

    def get_obj_marshaler(
            self,
            ty: ta.Any,
            *,
            no_cache: bool = False,
            **kwargs: ta.Any,
    ) -> ObjMarshaler:
        with self._lock:
            if not no_cache:
                try:
                    return self._obj_marshalers[ty]
                except KeyError:
                    pass

            try:
                return self._proxies[ty]
            except KeyError:
                pass

            rec = functools.partial(
                self.get_obj_marshaler,
                no_cache=no_cache,
                **kwargs,
            )

            p = ProxyObjMarshaler()
            self._proxies[ty] = p
            try:
                m = self.make_obj_marshaler(ty, rec, **kwargs)
            finally:
                del self._proxies[ty]
            p.m = m

            if not no_cache:
                self._obj_marshalers[ty] = m
            return m

    #

    def marshal_obj(
            self,
            o: ta.Any,
            ty: ta.Any = None,
            opts: ta.Optional[ObjMarshalOptions] = None,
    ) -> ta.Any:
        m = self.get_obj_marshaler(ty if ty is not None else type(o))
        return m.marshal(o, opts or self._default_options)

    def unmarshal_obj(
            self,
            o: ta.Any,
            ty: ta.Union[ta.Type[T], ta.Any],
            opts: ta.Optional[ObjMarshalOptions] = None,
    ) -> T:
        m = self.get_obj_marshaler(ty)
        return m.unmarshal(o, opts or self._default_options)

    def roundtrip_obj(
            self,
            o: ta.Any,
            ty: ta.Any = None,
            opts: ta.Optional[ObjMarshalOptions] = None,
    ) -> ta.Any:
        if ty is None:
            ty = type(o)
        m: ta.Any = self.marshal_obj(o, ty, opts)
        u: ta.Any = self.unmarshal_obj(m, ty, opts)
        return u


##


OBJ_MARSHALER_MANAGER = ObjMarshalerManager()

register_opj_marshaler = OBJ_MARSHALER_MANAGER.register_opj_marshaler
get_obj_marshaler = OBJ_MARSHALER_MANAGER.get_obj_marshaler

marshal_obj = OBJ_MARSHALER_MANAGER.marshal_obj
unmarshal_obj = OBJ_MARSHALER_MANAGER.unmarshal_obj


########################################
# ../../../omlish/lite/runtime.py


@cached_nullary
def is_debugger_attached() -> bool:
    return any(frame[1].endswith('pydevd.py') for frame in inspect.stack())


REQUIRED_PYTHON_VERSION = (3, 8)


def check_runtime_version() -> None:
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        raise OSError(f'Requires python {REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa


########################################
# ../bootstrap.py


@dc.dataclass(frozen=True)
class MainBootstrap:
    main_config: MainConfig = MainConfig()

    remote_config: RemoteConfig = RemoteConfig()


########################################
# ../commands/execution.py


CommandExecutorMap = ta.NewType('CommandExecutorMap', ta.Mapping[ta.Type[Command], CommandExecutor])


class CommandExecutionService(CommandExecutor):
    def __init__(
            self,
            *,
            command_executors: CommandExecutorMap,
    ) -> None:
        super().__init__()

        self._command_executors = command_executors

    def execute(self, cmd: Command) -> Command.Output:
        ce: CommandExecutor = self._command_executors[type(cmd)]
        return ce.execute(cmd)


########################################
# ../commands/marshal.py


def install_command_marshaling(
        cmds: CommandNameMap,
        msh: ObjMarshalerManager,
) -> None:
    for fn in [
        lambda c: c,
        lambda c: c.Output,
    ]:
        msh.register_opj_marshaler(
            fn(Command),
            PolymorphicObjMarshaler.of([
                PolymorphicObjMarshaler.Impl(
                    fn(cmd),
                    name,
                    msh.get_obj_marshaler(fn(cmd)),
                )
                for name, cmd in cmds.items()
            ]),
        )


########################################
# ../marshal.py


@dc.dataclass(frozen=True)
class ObjMarshalerInstaller:
    fn: ta.Callable[[ObjMarshalerManager], None]


ObjMarshalerInstallers = ta.NewType('ObjMarshalerInstallers', ta.Sequence[ObjMarshalerInstaller])


########################################
# ../remote/channel.py


class RemoteChannel:
    def __init__(
            self,
            input: ta.IO,  # noqa
            output: ta.IO,
            *,
            msh: ObjMarshalerManager = OBJ_MARSHALER_MANAGER,
    ) -> None:
        super().__init__()

        self._input = input
        self._output = output
        self._msh = msh

    def set_marshaler(self, msh: ObjMarshalerManager) -> None:
        self._msh = msh

    def send_obj(self, o: ta.Any, ty: ta.Any = None) -> None:
        j = json_dumps_compact(self._msh.marshal_obj(o, ty))
        d = j.encode('utf-8')

        self._output.write(struct.pack('<I', len(d)))
        self._output.write(d)
        self._output.flush()

    def recv_obj(self, ty: ta.Type[T]) -> ta.Optional[T]:
        d = self._input.read(4)
        if not d:
            return None
        if len(d) != 4:
            raise EOFError

        sz = struct.unpack('<I', d)[0]
        d = self._input.read(sz)
        if len(d) != sz:
            raise EOFError

        j = json.loads(d.decode('utf-8'))
        return self._msh.unmarshal_obj(j, ty)


########################################
# ../../../omlish/lite/subprocesses.py


##


SUBPROCESS_CHANNEL_OPTION_VALUES: ta.Mapping[SubprocessChannelOption, int] = {
    'pipe': subprocess.PIPE,
    'stdout': subprocess.STDOUT,
    'devnull': subprocess.DEVNULL,
}


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


@dc.dataclass(frozen=True)
class SubprocessCommand(Command['SubprocessCommand.Output']):
    cmd: ta.Sequence[str]

    shell: bool = False
    cwd: ta.Optional[str] = None
    env: ta.Optional[ta.Mapping[str, str]] = None

    stdout: str = 'pipe'  # SubprocessChannelOption
    stderr: str = 'pipe'  # SubprocessChannelOption

    input: ta.Optional[bytes] = None
    timeout: ta.Optional[float] = None

    def __post_init__(self) -> None:
        if isinstance(self.cmd, str):
            raise TypeError(self.cmd)

    @dc.dataclass(frozen=True)
    class Output(Command.Output):
        rc: int
        pid: int

        elapsed_s: float

        stdout: ta.Optional[bytes] = None
        stderr: ta.Optional[bytes] = None


##


class SubprocessCommandExecutor(CommandExecutor[SubprocessCommand, SubprocessCommand.Output]):
    def execute(self, inp: SubprocessCommand) -> SubprocessCommand.Output:
        with subprocess.Popen(
            subprocess_maybe_shell_wrap_exec(*inp.cmd),

            shell=inp.shell,
            cwd=inp.cwd,
            env={**os.environ, **(inp.env or {})},

            stdin=subprocess.PIPE if inp.input is not None else None,
            stdout=SUBPROCESS_CHANNEL_OPTION_VALUES[ta.cast(SubprocessChannelOption, inp.stdout)],
            stderr=SUBPROCESS_CHANNEL_OPTION_VALUES[ta.cast(SubprocessChannelOption, inp.stderr)],
        ) as proc:
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
# ../remote/spawning.py


class RemoteSpawning:
    @dc.dataclass(frozen=True)
    class Target:
        shell: ta.Optional[str] = None
        shell_quote: bool = False

        DEFAULT_PYTHON: ta.ClassVar[str] = 'python3'
        python: str = DEFAULT_PYTHON

        stderr: ta.Optional[str] = None  # SubprocessChannelOption

    #

    class _PreparedCmd(ta.NamedTuple):
        cmd: ta.Sequence[str]
        shell: bool

    def _prepare_cmd(
            self,
            tgt: Target,
            src: str,
    ) -> _PreparedCmd:
        if tgt.shell is not None:
            sh_src = f'{tgt.python} -c {shlex.quote(src)}'
            if tgt.shell_quote:
                sh_src = shlex.quote(sh_src)
            sh_cmd = f'{tgt.shell} {sh_src}'
            return RemoteSpawning._PreparedCmd(
                cmd=[sh_cmd],
                shell=True,
            )

        else:
            return RemoteSpawning._PreparedCmd(
                cmd=[tgt.python, '-c', src],
                shell=False,
            )

    #

    @dc.dataclass(frozen=True)
    class Spawned:
        stdin: ta.IO
        stdout: ta.IO
        stderr: ta.Optional[ta.IO]

    @contextlib.contextmanager
    def spawn(
            self,
            tgt: Target,
            src: str,
            *,
            timeout: ta.Optional[float] = None,
    ) -> ta.Generator[Spawned, None, None]:
        pc = self._prepare_cmd(tgt, src)

        with subprocess.Popen(
            subprocess_maybe_shell_wrap_exec(*pc.cmd),
            shell=pc.shell,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=(
                SUBPROCESS_CHANNEL_OPTION_VALUES[ta.cast(SubprocessChannelOption, tgt.stderr)]
                if tgt.stderr is not None else None
            ),
        ) as proc:
            stdin = check_not_none(proc.stdin)
            stdout = check_not_none(proc.stdout)

            try:
                yield RemoteSpawning.Spawned(
                    stdin=stdin,
                    stdout=stdout,
                    stderr=proc.stderr,
                )

            finally:
                try:
                    stdin.close()
                except BrokenPipeError:
                    pass

                proc.wait(timeout)


########################################
# ../commands/inject.py


##


def bind_command(
        command_cls: ta.Type[Command],
        executor_cls: ta.Optional[ta.Type[CommandExecutor]],
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(CommandRegistration(command_cls), array=True),
    ]

    if executor_cls is not None:
        lst.extend([
            inj.bind(executor_cls, singleton=True),
            inj.bind(CommandExecutorRegistration(command_cls, executor_cls), array=True),
        ])

    return inj.as_bindings(*lst)


##


@dc.dataclass(frozen=True)
class _FactoryCommandExecutor(CommandExecutor):
    factory: ta.Callable[[], CommandExecutor]

    def execute(self, i: Command) -> Command.Output:
        return self.factory().execute(i)


##


def bind_commands(
        *,
        main_config: MainConfig,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind_array(CommandRegistration),
        inj.bind_array_type(CommandRegistration, CommandRegistrations),

        inj.bind_array(CommandExecutorRegistration),
        inj.bind_array_type(CommandExecutorRegistration, CommandExecutorRegistrations),

        inj.bind(build_command_name_map, singleton=True),
    ]

    #

    def provide_obj_marshaler_installer(cmds: CommandNameMap) -> ObjMarshalerInstaller:
        return ObjMarshalerInstaller(functools.partial(install_command_marshaling, cmds))

    lst.append(inj.bind(provide_obj_marshaler_installer, array=True))

    #

    def provide_command_executor_map(
            injector: Injector,
            crs: CommandExecutorRegistrations,
    ) -> CommandExecutorMap:
        dct: ta.Dict[ta.Type[Command], CommandExecutor] = {}

        cr: CommandExecutorRegistration
        for cr in crs:
            if cr.command_cls in dct:
                raise KeyError(cr.command_cls)

            factory = functools.partial(injector.provide, cr.executor_cls)
            if main_config.debug:
                ce = factory()
            else:
                ce = _FactoryCommandExecutor(factory)

            dct[cr.command_cls] = ce

        return CommandExecutorMap(dct)

    lst.extend([
        inj.bind(provide_command_executor_map, singleton=True),

        inj.bind(CommandExecutionService, singleton=True, eager=main_config.debug),
        inj.bind(CommandExecutor, to_key=CommandExecutionService),
    ])

    #

    for command_cls, executor_cls in [
        (SubprocessCommand, SubprocessCommandExecutor),
    ]:
        lst.append(bind_command(command_cls, executor_cls))

    #

    return inj.as_bindings(*lst)


########################################
# ../remote/execution.py


##


def _remote_execution_main() -> None:
    rt = pyremote_bootstrap_finalize()  # noqa

    chan = RemoteChannel(
        rt.input,
        rt.output,
    )

    bs = check_not_none(chan.recv_obj(MainBootstrap))

    if (prd := bs.remote_config.pycharm_remote_debug) is not None:
        pycharm_debug_connect(prd)

    injector = main_bootstrap(bs)

    chan.set_marshaler(injector[ObjMarshalerManager])

    ce = injector[CommandExecutor]

    while True:
        i = chan.recv_obj(Command)
        if i is None:
            break

        r = ce.try_execute(
            i,
            log=log,
            omit_exc_object=True,
        )

        chan.send_obj(r)


##


@dc.dataclass()
class RemoteCommandError(Exception):
    e: CommandException


class RemoteCommandExecutor(CommandExecutor):
    def __init__(self, chan: RemoteChannel) -> None:
        super().__init__()

        self._chan = chan

    def _remote_execute(self, cmd: Command) -> CommandOutputOrException:
        self._chan.send_obj(cmd, Command)

        if (r := self._chan.recv_obj(CommandOutputOrExceptionData)) is None:
            raise EOFError

        return r

    # @ta.override
    def execute(self, cmd: Command) -> Command.Output:
        r = self._remote_execute(cmd)
        if (e := r.exception) is not None:
            raise RemoteCommandError(e)
        else:
            return check_not_none(r.output)

    # @ta.override
    def try_execute(
            self,
            cmd: Command,
            *,
            log: ta.Optional[logging.Logger] = None,
            omit_exc_object: bool = False,
    ) -> CommandOutputOrException:
        try:
            r = self._remote_execute(cmd)

        except Exception as e:  # noqa
            if log is not None:
                log.exception('Exception executing remote command: %r', type(cmd))

            return CommandOutputOrExceptionData(exception=CommandException.of(
                e,
                omit_exc_object=omit_exc_object,
                cmd=cmd,
            ))

        else:
            return r


##


class RemoteExecution:
    def __init__(
            self,
            *,
            spawning: RemoteSpawning,
            msh: ObjMarshalerManager,
            payload_file: ta.Optional[RemoteExecutionPayloadFile] = None,
    ) -> None:
        super().__init__()

        self._spawning = spawning
        self._msh = msh
        self._payload_file = payload_file

    #

    @cached_nullary
    def _payload_src(self) -> str:
        return get_remote_payload_src(file=self._payload_file)

    @cached_nullary
    def _remote_src(self) -> ta.Sequence[str]:
        return [
            self._payload_src(),
            '_remote_execution_main()',
        ]

    @cached_nullary
    def _spawn_src(self) -> str:
        return pyremote_build_bootstrap_cmd(__package__ or 'manage')

    #

    @contextlib.contextmanager
    def connect(
            self,
            tgt: RemoteSpawning.Target,
            bs: MainBootstrap,
    ) -> ta.Generator[RemoteCommandExecutor, None, None]:
        spawn_src = self._spawn_src()
        remote_src = self._remote_src()

        with self._spawning.spawn(
                tgt,
                spawn_src,
        ) as proc:
            res = PyremoteBootstrapDriver(  # noqa
                remote_src,
                PyremoteBootstrapOptions(
                    debug=bs.main_config.debug,
                ),
            ).run(
                proc.stdout,
                proc.stdin,
            )

            chan = RemoteChannel(
                proc.stdout,
                proc.stdin,
                msh=self._msh,
            )

            chan.send_obj(bs)

            yield RemoteCommandExecutor(chan)


########################################
# ../remote/inject.py


def bind_remote(
        *,
        remote_config: RemoteConfig,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(remote_config),

        inj.bind(RemoteSpawning, singleton=True),

        inj.bind(RemoteExecution, singleton=True),
    ]

    if (pf := remote_config.payload_file) is not None:
        lst.append(inj.bind(pf, to_key=RemoteExecutionPayloadFile))

    return inj.as_bindings(*lst)


########################################
# ../inject.py


##


def bind_main(
        *,
        main_config: MainConfig,
        remote_config: RemoteConfig,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(main_config),

        bind_commands(
            main_config=main_config,
        ),

        bind_remote(
            remote_config=remote_config,
        ),
    ]

    #

    def build_obj_marshaler_manager(insts: ObjMarshalerInstallers) -> ObjMarshalerManager:
        msh = ObjMarshalerManager()
        inst: ObjMarshalerInstaller
        for inst in insts:
            inst.fn(msh)
        return msh

    lst.extend([
        inj.bind(build_obj_marshaler_manager, singleton=True),

        inj.bind_array(ObjMarshalerInstaller),
        inj.bind_array_type(ObjMarshalerInstaller, ObjMarshalerInstallers),
    ])

    #

    return inj.as_bindings(*lst)


########################################
# ../bootstrap_.py


def main_bootstrap(bs: MainBootstrap) -> Injector:
    if (log_level := bs.main_config.log_level) is not None:
        configure_standard_logging(log_level)

    injector = inj.create_injector(bind_main(  # noqa
        main_config=bs.main_config,
        remote_config=bs.remote_config,
    ))

    return injector


########################################
# main.py


##


def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--_payload-file')

    parser.add_argument('-s', '--shell')
    parser.add_argument('-q', '--shell-quote', action='store_true')
    parser.add_argument('--python', default='python3')

    parser.add_argument('--pycharm-debug-port', type=int)
    parser.add_argument('--pycharm-debug-host')
    parser.add_argument('--pycharm-debug-version')

    parser.add_argument('--debug', action='store_true')

    parser.add_argument('command', nargs='+')

    args = parser.parse_args()

    #

    bs = MainBootstrap(
        main_config=MainConfig(
            log_level='DEBUG' if args.debug else 'INFO',

            debug=bool(args.debug),
        ),

        remote_config=RemoteConfig(
            payload_file=args._payload_file,  # noqa

            pycharm_remote_debug=PycharmRemoteDebug(
                port=args.pycharm_debug_port,
                host=args.pycharm_debug_host,
                install_version=args.pycharm_debug_version,
            ) if args.pycharm_debug_port is not None else None,
        ),
    )

    injector = main_bootstrap(
        bs,
    )

    #

    cmds = [
        # SubprocessCommand(['python3', '-'], input=b'print(1)\n'),
        # SubprocessCommand(['uname']),
        # SubprocessCommand(['barf']),
        SubprocessCommand([c])
        for c in args.command
    ]

    ce = injector[CommandExecutor]
    msh = injector[ObjMarshalerManager]
    for cmd in cmds:
        mc = msh.roundtrip_obj(cmd, Command)
        r = ce.try_execute(
            mc,
            log=log,
            omit_exc_object=True,
        )
        mr = msh.roundtrip_obj(r, CommandOutputOrExceptionData)
        print(mr)

    #

    tgt = RemoteSpawning.Target(
        shell=args.shell,
        shell_quote=args.shell_quote,
        python=args.python,
    )

    with injector[RemoteExecution].connect(tgt, bs) as rce:
        for cmd in cmds:
            r = rce.try_execute(cmd)

            print(json_dumps_pretty(msh.marshal_obj(r)))

    #

    print('Success')


if __name__ == '__main__':
    _main()
