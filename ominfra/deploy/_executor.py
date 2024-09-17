#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omlish-lite
# @omlish-script
# @omdev-amalg-output executor/main.py
# ruff: noqa: N802 UP006 UP007 UP036
r"""
TODO:
 - flock
 - interp.py
 - systemd

deployment matrix
 - os: ubuntu / amzn / generic
 - arch: amd64 / arm64
 - host: bare / docker
 - init: supervisor-provided / supervisor-must-configure / systemd (/ self?)
 - interp: system / pyenv / interp.py
 - venv: none / yes
 - nginx: no / provided / must-configure

==

~deploy
  deploy.pid (flock)
  /app
    /<appspec> - shallow clone
  /conf
    /env
      <appspec>.env
    /nginx
      <appspec>.conf
    /supervisor
      <appspec>.conf
  /venv
    /<appspec>

?
  /logs
    /wrmsr--omlish--<spec>

spec = <name>--<rev>--<when>

https://docs.docker.com/config/containers/multi-service_container/#use-a-process-manager
https://serverfault.com/questions/211525/supervisor-not-loading-new-configuration-files
"""  # noqa
import abc
import argparse
import base64
import collections.abc
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
import os.path
import pwd
import shlex
import subprocess
import sys
import textwrap
import threading
import typing as ta
import uuid
import weakref  # noqa


########################################


if sys.version_info < (3, 8):
    raise OSError(
        f'Requires python (3, 8), got {sys.version_info} from {sys.executable}')  # noqa


########################################


# ../../../../omlish/lite/check.py
T = ta.TypeVar('T')


########################################
# ../../configs.py


@dc.dataclass(frozen=True)
class DeployConfig:
    python_bin: str
    app_name: str
    repo_url: str
    revision: str
    requirements_txt: str
    entrypoint: str


@dc.dataclass(frozen=True)
class HostConfig:
    username: str = 'deploy'

    global_supervisor_conf_file_path: str = '/etc/supervisor/conf.d/supervisord.conf'
    global_nginx_conf_file_path: str = '/etc/nginx/sites-enabled/deploy.conf'


########################################
# ../../../../omlish/lite/cached.py


class cached_nullary:  # noqa
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


########################################
# ../../../../omlish/lite/check.py


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
# ../../../../omlish/lite/reflect.py


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


def configure_standard_logging(
        level: ta.Union[int, str] = logging.INFO,
        *,
        json: bool = False,
        target: ta.Optional[logging.Logger] = None,
        force: bool = False,
) -> ta.Optional[StandardLogHandler]:
    logging._acquireLock()  # type: ignore  # noqa
    try:
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

    finally:
        logging._releaseLock()  # type: ignore  # noqa


########################################
# ../../../../omlish/lite/marshal.py
"""
TODO:
 - pickle stdlib objs? have to pin to 3.8 pickle protocol, will be cross-version
 - nonstrict toggle
"""


##


class ObjMarshaler(abc.ABC):
    @abc.abstractmethod
    def marshal(self, o: ta.Any) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def unmarshal(self, o: ta.Any) -> ta.Any:
        raise NotImplementedError


class NopObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any) -> ta.Any:
        return o

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return o


@dc.dataclass()
class ProxyObjMarshaler(ObjMarshaler):
    m: ta.Optional[ObjMarshaler] = None

    def marshal(self, o: ta.Any) -> ta.Any:
        return check_not_none(self.m).marshal(o)

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return check_not_none(self.m).unmarshal(o)


@dc.dataclass(frozen=True)
class CastObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any) -> ta.Any:
        return o

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty(o)


class DynamicObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any) -> ta.Any:
        return marshal_obj(o)

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return o


@dc.dataclass(frozen=True)
class Base64ObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any) -> ta.Any:
        return base64.b64encode(o).decode('ascii')

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty(base64.b64decode(o))


@dc.dataclass(frozen=True)
class EnumObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any) -> ta.Any:
        return o.name

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty.__members__[o]  # type: ignore


@dc.dataclass(frozen=True)
class OptionalObjMarshaler(ObjMarshaler):
    item: ObjMarshaler

    def marshal(self, o: ta.Any) -> ta.Any:
        if o is None:
            return None
        return self.item.marshal(o)

    def unmarshal(self, o: ta.Any) -> ta.Any:
        if o is None:
            return None
        return self.item.unmarshal(o)


@dc.dataclass(frozen=True)
class MappingObjMarshaler(ObjMarshaler):
    ty: type
    km: ObjMarshaler
    vm: ObjMarshaler

    def marshal(self, o: ta.Any) -> ta.Any:
        return {self.km.marshal(k): self.vm.marshal(v) for k, v in o.items()}

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty((self.km.unmarshal(k), self.vm.unmarshal(v)) for k, v in o.items())


@dc.dataclass(frozen=True)
class IterableObjMarshaler(ObjMarshaler):
    ty: type
    item: ObjMarshaler

    def marshal(self, o: ta.Any) -> ta.Any:
        return [self.item.marshal(e) for e in o]

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty(self.item.unmarshal(e) for e in o)


@dc.dataclass(frozen=True)
class DataclassObjMarshaler(ObjMarshaler):
    ty: type
    fs: ta.Mapping[str, ObjMarshaler]
    nonstrict: bool = False

    def marshal(self, o: ta.Any) -> ta.Any:
        return {k: m.marshal(getattr(o, k)) for k, m in self.fs.items()}

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty(**{k: self.fs[k].unmarshal(v) for k, v in o.items() if self.nonstrict or k in self.fs})


@dc.dataclass(frozen=True)
class PolymorphicObjMarshaler(ObjMarshaler):
    class Impl(ta.NamedTuple):
        ty: type
        tag: str
        m: ObjMarshaler

    impls_by_ty: ta.Mapping[type, Impl]
    impls_by_tag: ta.Mapping[str, Impl]

    def marshal(self, o: ta.Any) -> ta.Any:
        impl = self.impls_by_ty[type(o)]
        return {impl.tag: impl.m.marshal(o)}

    def unmarshal(self, o: ta.Any) -> ta.Any:
        [(t, v)] = o.items()
        impl = self.impls_by_tag[t]
        return impl.m.unmarshal(v)


@dc.dataclass(frozen=True)
class DatetimeObjMarshaler(ObjMarshaler):
    ty: type

    def marshal(self, o: ta.Any) -> ta.Any:
        return o.isoformat()

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty.fromisoformat(o)  # type: ignore


class DecimalObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any) -> ta.Any:
        return str(check_isinstance(o, decimal.Decimal))

    def unmarshal(self, v: ta.Any) -> ta.Any:
        return decimal.Decimal(check_isinstance(v, str))


class FractionObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any) -> ta.Any:
        fr = check_isinstance(o, fractions.Fraction)
        return [fr.numerator, fr.denominator]

    def unmarshal(self, v: ta.Any) -> ta.Any:
        num, denom = check_isinstance(v, list)
        return fractions.Fraction(num, denom)


class UuidObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any) -> ta.Any:
        return str(o)

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return uuid.UUID(o)


_OBJ_MARSHALERS: ta.Dict[ta.Any, ObjMarshaler] = {
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


def register_opj_marshaler(ty: ta.Any, m: ObjMarshaler) -> None:
    if ty in _OBJ_MARSHALERS:
        raise KeyError(ty)
    _OBJ_MARSHALERS[ty] = m


def _make_obj_marshaler(ty: ta.Any) -> ObjMarshaler:
    if isinstance(ty, type) and abc.ABC in ty.__bases__:
        impls = [  # type: ignore
            PolymorphicObjMarshaler.Impl(
                ity,
                ity.__qualname__,
                get_obj_marshaler(ity),
            )
            for ity in deep_subclasses(ty)
            if abc.ABC not in ity.__bases__
        ]
        return PolymorphicObjMarshaler(
            {i.ty: i for i in impls},
            {i.tag: i for i in impls},
        )

    if isinstance(ty, type) and issubclass(ty, enum.Enum):
        return EnumObjMarshaler(ty)

    if dc.is_dataclass(ty):
        return DataclassObjMarshaler(
            ty,
            {f.name: get_obj_marshaler(f.type) for f in dc.fields(ty)},
        )

    if is_generic_alias(ty):
        try:
            mt = _OBJ_MARSHALER_GENERIC_MAPPING_TYPES[ta.get_origin(ty)]
        except KeyError:
            pass
        else:
            k, v = ta.get_args(ty)
            return MappingObjMarshaler(mt, get_obj_marshaler(k), get_obj_marshaler(v))

        try:
            st = _OBJ_MARSHALER_GENERIC_ITERABLE_TYPES[ta.get_origin(ty)]
        except KeyError:
            pass
        else:
            [e] = ta.get_args(ty)
            return IterableObjMarshaler(st, get_obj_marshaler(e))

        if is_union_alias(ty):
            return OptionalObjMarshaler(get_obj_marshaler(get_optional_alias_arg(ty)))

    raise TypeError(ty)


def get_obj_marshaler(ty: ta.Any) -> ObjMarshaler:
    try:
        return _OBJ_MARSHALERS[ty]
    except KeyError:
        pass

    p = ProxyObjMarshaler()
    _OBJ_MARSHALERS[ty] = p
    try:
        m = _make_obj_marshaler(ty)
    except Exception:
        del _OBJ_MARSHALERS[ty]
        raise
    else:
        p.m = m
        _OBJ_MARSHALERS[ty] = m
        return m


def marshal_obj(o: ta.Any, ty: ta.Any = None) -> ta.Any:
    return get_obj_marshaler(ty if ty is not None else type(o)).marshal(o)


def unmarshal_obj(o: ta.Any, ty: ta.Union[ta.Type[T], ta.Any]) -> T:
    return get_obj_marshaler(ty).unmarshal(o)


########################################
# ../../../../omlish/lite/runtime.py


@cached_nullary
def is_debugger_attached() -> bool:
    return any(frame[1].endswith('pydevd.py') for frame in inspect.stack())


REQUIRED_PYTHON_VERSION = (3, 8)


def check_runtime_version() -> None:
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        raise OSError(
            f'Requires python {REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa


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


########################################
# ../base.py


##


class Phase(enum.Enum):
    HOST = enum.auto()
    ENV = enum.auto()
    BACKEND = enum.auto()
    FRONTEND = enum.auto()
    START_BACKEND = enum.auto()
    START_FRONTEND = enum.auto()


def run_in_phase(*ps: Phase):
    def inner(fn):
        fn.__deployment_phases__ = ps
        return fn
    return inner


class Concern(abc.ABC):
    def __init__(self, d: 'Deployment') -> None:
        super().__init__()
        self._d = d

    _phase_fns: ta.ClassVar[ta.Mapping[Phase, ta.Sequence[ta.Callable]]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        dct: ta.Dict[Phase, ta.List[ta.Callable]] = {}
        for fn, ps in [
            (v, ps)
            for a in dir(cls)
            if not (a.startswith('__') and a.endswith('__'))
            for v in [getattr(cls, a, None)]
            for ps in [getattr(v, '__deployment_phases__', None)]
            if ps
        ]:
            dct.update({p: [*dct.get(p, []), fn] for p in ps})
        cls._phase_fns = dct

    @dc.dataclass(frozen=True)
    class Output(abc.ABC):
        path: str
        is_file: bool

    def outputs(self) -> ta.Sequence[Output]:
        return ()

    def run_phase(self, p: Phase) -> None:
        for fn in self._phase_fns.get(p, ()):
            fn.__get__(self, type(self))()


##


class Deployment:

    def __init__(
            self,
            cfg: DeployConfig,
            concern_cls_list: ta.List[ta.Type[Concern]],
            host_cfg: HostConfig = HostConfig(),
    ) -> None:
        super().__init__()
        self._cfg = cfg
        self._host_cfg = host_cfg

        self._concerns: ta.List[Concern] = [cls(self) for cls in concern_cls_list]

    @property
    def cfg(self) -> DeployConfig:
        return self._cfg

    @property
    def host_cfg(self) -> HostConfig:
        return self._host_cfg

    def sh(self, *ss: str) -> None:
        s = ' && '.join(ss)
        log.info('Executing: %s', s)
        subprocess_check_call(s, shell=True)

    def ush(self, *ss: str) -> None:
        s = ' && '.join(ss)
        self.sh(f'su - {self._host_cfg.username} -c {shlex.quote(s)}')

    @cached_nullary
    def home_dir(self) -> str:
        return os.path.expanduser(f'~{self._host_cfg.username}')

    @cached_nullary
    def deploy(self) -> None:
        for p in Phase:
            log.info('Phase %s', p.name)
            for c in self._concerns:
                c.run_phase(p)

        log.info('Shitty deploy complete!')


########################################
# ../concerns/dirs.py


class DirsConcern(Concern):
    @run_in_phase(Phase.HOST)
    def create_dirs(self) -> None:
        pwn = pwd.getpwnam(self._d.host_cfg.username)

        for dn in [
            'app',
            'conf',
            'conf/env',
            'conf/nginx',
            'conf/supervisor',
            'venv',
        ]:
            fp = os.path.join(self._d.home_dir(), dn)
            if not os.path.exists(fp):
                log.info('Creating directory: %s', fp)
                os.mkdir(fp)
                os.chown(fp, pwn.pw_uid, pwn.pw_gid)


########################################
# ../concerns/nginx.py
"""
TODO:
 - https://stackoverflow.com/questions/3011067/restart-nginx-without-sudo
"""


class GlobalNginxConcern(Concern):
    @run_in_phase(Phase.HOST)
    def create_global_nginx_conf(self) -> None:
        nginx_conf_dir = os.path.join(self._d.home_dir(), 'conf/nginx')
        if not os.path.isfile(self._d.host_cfg.global_nginx_conf_file_path):
            log.info('Writing global nginx conf at %s', self._d.host_cfg.global_nginx_conf_file_path)
            with open(self._d.host_cfg.global_nginx_conf_file_path, 'w') as f:
                f.write(f'include {nginx_conf_dir}/*.conf;\n')


class NginxConcern(Concern):
    @run_in_phase(Phase.FRONTEND)
    def create_nginx_conf(self) -> None:
        nginx_conf = textwrap.dedent(f"""
            server {{
                listen 80;
                location / {{
                    proxy_pass http://127.0.0.1:8000/;
                }}
            }}
        """)
        nginx_conf_file = os.path.join(self._d.home_dir(), f'conf/nginx/{self._d.cfg.app_name}.conf')
        log.info('Writing nginx conf to %s', nginx_conf_file)
        with open(nginx_conf_file, 'w') as f:
            f.write(nginx_conf)

    @run_in_phase(Phase.START_FRONTEND)
    def poke_nginx(self) -> None:
        log.info('Starting nginx')
        self._d.sh('service nginx start')

        log.info('Poking nginx')
        self._d.sh('nginx -s reload')


########################################
# ../concerns/repo.py


class RepoConcern(Concern):
    @run_in_phase(Phase.ENV)
    def clone_repo(self) -> None:
        clone_submodules = False
        self._d.ush(
            'cd ~/app',
            f'git clone --depth 1 {self._d.cfg.repo_url} {self._d.cfg.app_name}',
            *([
                f'cd {self._d.cfg.app_name}',
                'git submodule update --init',
            ] if clone_submodules else []),
        )


########################################
# ../concerns/supervisor.py


class GlobalSupervisorConcern(Concern):
    @run_in_phase(Phase.HOST)
    def create_global_supervisor_conf(self) -> None:
        sup_conf_dir = os.path.join(self._d.home_dir(), 'conf/supervisor')
        with open(self._d.host_cfg.global_supervisor_conf_file_path) as f:
            glo_sup_conf = f.read()
        if sup_conf_dir not in glo_sup_conf:
            log.info('Updating global supervisor conf at %s', self._d.host_cfg.global_supervisor_conf_file_path)  # noqa
            glo_sup_conf += textwrap.dedent(f"""
                [include]
                files = {self._d.home_dir()}/conf/supervisor/*.conf
            """)
            with open(self._d.host_cfg.global_supervisor_conf_file_path, 'w') as f:
                f.write(glo_sup_conf)


class SupervisorConcern(Concern):
    @run_in_phase(Phase.BACKEND)
    def create_supervisor_conf(self) -> None:
        sup_conf = textwrap.dedent(f"""
            [program:{self._d.cfg.app_name}]
            command={self._d.home_dir()}/venv/{self._d.cfg.app_name}/bin/python -m {self._d.cfg.entrypoint}
            directory={self._d.home_dir()}/app/{self._d.cfg.app_name}
            user={self._d.host_cfg.username}
            autostart=true
            autorestart=true
        """)
        sup_conf_file = os.path.join(self._d.home_dir(), f'conf/supervisor/{self._d.cfg.app_name}.conf')
        log.info('Writing supervisor conf to %s', sup_conf_file)
        with open(sup_conf_file, 'w') as f:
            f.write(sup_conf)

    @run_in_phase(Phase.START_BACKEND)
    def poke_supervisor(self) -> None:
        log.info('Poking supervisor')
        self._d.sh('kill -HUP 1')


########################################
# ../concerns/user.py


class UserConcern(Concern):
    @run_in_phase(Phase.HOST)
    def create_user(self) -> None:
        try:
            pwd.getpwnam(self._d.host_cfg.username)
        except KeyError:
            log.info('Creating user %s', self._d.host_cfg.username)
            self._d.sh(' '.join([
                'adduser',
                '--system',
                '--disabled-password',
                '--group',
                '--shell /bin/bash',
                self._d.host_cfg.username,
            ]))
            pwd.getpwnam(self._d.host_cfg.username)


########################################
# ../concerns/venv.py
"""
TODO:
 - use LinuxInterpResolver lol
"""


class VenvConcern(Concern):
    @run_in_phase(Phase.ENV)
    def setup_venv(self) -> None:
        self._d.ush(
            'cd ~/venv',
            f'{self._d.cfg.python_bin} -mvenv {self._d.cfg.app_name}',

            # https://stackoverflow.com/questions/77364550/attributeerror-module-pkgutil-has-no-attribute-impimporter-did-you-mean
            f'{self._d.cfg.app_name}/bin/python -m ensurepip',
            f'{self._d.cfg.app_name}/bin/python -mpip install --upgrade setuptools pip',

            f'{self._d.cfg.app_name}/bin/python -mpip install -r ~deploy/app/{self._d.cfg.app_name}/{self._d.cfg.requirements_txt}',  # noqa
        )


########################################
# main.py


##


def _deploy_cmd(args) -> None:
    dct = json.loads(args.cfg)
    cfg: DeployConfig = unmarshal_obj(dct, DeployConfig)
    dp = Deployment(
        cfg,
        [
            UserConcern,
            DirsConcern,
            GlobalNginxConcern,
            GlobalSupervisorConcern,
            RepoConcern,
            VenvConcern,
            SupervisorConcern,
            NginxConcern,
        ],
    )
    dp.deploy()


##


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    parser_resolve = subparsers.add_parser('deploy')
    parser_resolve.add_argument('cfg')
    parser_resolve.set_defaults(func=_deploy_cmd)

    return parser


def _main(argv: ta.Optional[ta.Sequence[str]] = None) -> None:
    check_runtime_version()

    if getattr(sys, 'platform') != 'linux':  # noqa
        raise OSError('must run on linux')

    configure_standard_logging()

    parser = _build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func(args)


if __name__ == '__main__':
    _main()
