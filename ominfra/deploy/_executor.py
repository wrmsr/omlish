#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omdev-amalg-output executor/main.py
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
# ruff: noqa: UP007
import abc
import argparse
import base64
import collections.abc
import dataclasses as dc
import datetime
import enum
import functools
import json
import logging
import os
import os.path
import pwd
import shlex
import shutil
import subprocess
import sys
import textwrap
import typing as ta
import uuid
import weakref  # noqa


T = ta.TypeVar('T')


########################################
# ../../../../omdev/amalg/std/cached.py


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
# ../../../../omdev/amalg/std/check.py
# ruff: noqa: UP006 UP007


def check_isinstance(v: T, spec: ta.Union[ta.Type[T], tuple]) -> T:
    if not isinstance(v, spec):
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


########################################
# ../../../../omdev/amalg/std/logs.py
"""
TODO:
 - debug
"""


log = logging.getLogger(__name__)


def configure_standard_logging() -> None:
    logging.root.addHandler(logging.StreamHandler())
    logging.root.setLevel('INFO')


########################################
# ../../../../omdev/amalg/std/reflect.py


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


########################################
# ../../../../omdev/amalg/std/runtime.py


REQUIRED_PYTHON_VERSION = (3, 8)


def check_runtime_version() -> None:
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        raise OSError(
            f'Requires python {REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa


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
# ../../../../omdev/amalg/std/marshal.py
"""
TODO:
 - pickle stdlib objs? have to pin to 3.8 pickle protocol, will be cross-version
"""
# ruff: noqa: UP006 UP007


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
class SequenceObjMarshaler(ObjMarshaler):
    ty: type
    item: ObjMarshaler

    def marshal(self, o: ta.Any) -> ta.Any:
        return [self.item.marshal(e) for e in o]

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty(self.item.unmarshal(e) for e in o)


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
class DataclassObjMarshaler(ObjMarshaler):
    ty: type
    fs: ta.Mapping[str, ObjMarshaler]

    def marshal(self, o: ta.Any) -> ta.Any:
        return {k: m.marshal(getattr(o, k)) for k, m in self.fs.items()}

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return self.ty(**{k: m.unmarshal(o[k]) for k, m in self.fs.items()})


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


class UuidObjMarshaler(ObjMarshaler):
    def marshal(self, o: ta.Any) -> ta.Any:
        return str(o)

    def unmarshal(self, o: ta.Any) -> ta.Any:
        return uuid.UUID(o)


_OBJ_MARSHALERS: ta.Dict[ta.Any, ObjMarshaler] = {
    **{t: NopObjMarshaler() for t in (type(None),)},
    **{t: CastObjMarshaler(t) for t in (int, float, str)},
    **{t: Base64ObjMarshaler(t) for t in (bytes, bytearray)},
    **{t: SequenceObjMarshaler(t, DynamicObjMarshaler()) for t in (list, tuple, set, frozenset)},
    **{t: MappingObjMarshaler(t, DynamicObjMarshaler(), DynamicObjMarshaler()) for t in (dict,)},

    ta.Any: DynamicObjMarshaler(),

    **{t: DatetimeObjMarshaler(t) for t in (datetime.date, datetime.time, datetime.datetime)},
    uuid.UUID: UuidObjMarshaler(),
}

_OBJ_MARSHALER_GENERIC_SEQUENCE_TYPES: ta.Dict[ta.Any, type] = {
    **{t: t for t in (list, tuple, set, frozenset)},
    **{t: frozenset for t in (collections.abc.Set, collections.abc.MutableSet)},
    **{t: tuple for t in (collections.abc.Sequence, collections.abc.MutableSequence)},
}

_OBJ_MARSHALER_GENERIC_MAPPING_TYPES: ta.Dict[ta.Any, type] = {
    **{t: t for t in (dict,)},
    **{t: dict for t in (collections.abc.Mapping, collections.abc.MutableMapping)},
}


def register_opj_marshaler(ty: ta.Any, m: ObjMarshaler) -> None:
    if ty in _OBJ_MARSHALERS:
        raise KeyError(ty)
    _OBJ_MARSHALERS[ty] = m


def _make_obj_marshaler(ty: ta.Any) -> ObjMarshaler:
    if isinstance(ty, type) and abc.ABC in ty.__bases__:
        impls = [
            PolymorphicObjMarshaler.Impl(
                ity,
                ity.__name__,
                get_obj_marshaler(ity),
            )
            for ity in ty.__subclasses__()
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
            st = _OBJ_MARSHALER_GENERIC_SEQUENCE_TYPES[ta.get_origin(ty)]
        except KeyError:
            pass
        else:
            [e] = ta.get_args(ty)
            return SequenceObjMarshaler(st, get_obj_marshaler(e))

        try:
            mt = _OBJ_MARSHALER_GENERIC_MAPPING_TYPES[ta.get_origin(ty)]
        except KeyError:
            pass
        else:
            k, v = ta.get_args(ty)
            return MappingObjMarshaler(mt, get_obj_marshaler(k), get_obj_marshaler(v))

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


def unmarshal_obj(o: ta.Any, ty: ta.Any) -> ta.Any:
    return get_obj_marshaler(ty).unmarshal(o)


########################################
# ../../../../omdev/amalg/std/subprocesses.py
# ruff: noqa: UP006 UP007


##


def _prepare_subprocess_invocation(
        *args: ta.Any,
        env: ta.Optional[ta.Mapping[str, ta.Any]] = None,
        extra_env: ta.Optional[ta.Mapping[str, ta.Any]] = None,
        **kwargs: ta.Any,
) -> ta.Tuple[ta.Tuple[ta.Any, ...], ta.Dict[str, ta.Any]]:
    log.debug(args)
    if extra_env:
        log.debug(extra_env)

    if extra_env:
        env = {**(env if env is not None else os.environ), **extra_env}

    return args, dict(
        env=env,
        **kwargs,
    )


def subprocess_check_call(*args: ta.Any, stdout=sys.stderr, **kwargs: ta.Any) -> None:
    args, kwargs = _prepare_subprocess_invocation(*args, stdout=stdout, **kwargs)
    return subprocess.check_call(args, **kwargs)  # type: ignore


def subprocess_check_output(*args: ta.Any, **kwargs: ta.Any) -> bytes:
    args, kwargs = _prepare_subprocess_invocation(*args, **kwargs)
    return subprocess.check_output(args, **kwargs)


def subprocess_check_output_str(*args: ta.Any, **kwargs: ta.Any) -> str:
    return subprocess_check_output(*args, **kwargs).decode().strip()


##


DEFAULT_SUBPROCESS_TRY_EXCEPTIONS: ta.Tuple[ta.Type[Exception], ...] = (
    FileNotFoundError,
    subprocess.CalledProcessError,
)


def subprocess_try_call(
        *args: ta.Any,
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
        *args: ta.Any,
        try_exceptions: ta.Tuple[ta.Type[Exception], ...] = DEFAULT_SUBPROCESS_TRY_EXCEPTIONS,
        **kwargs: ta.Any,
) -> ta.Optional[bytes]:
    try:
        return subprocess_check_output(*args, **kwargs)
    except try_exceptions as e:  # noqa
        if log.isEnabledFor(logging.DEBUG):
            log.exception('command failed')
        return None


def subprocess_try_output_str(*args: ta.Any, **kwargs: ta.Any) -> ta.Optional[str]:
    out = subprocess_try_output(*args, **kwargs)
    return out.decode().strip() if out is not None else None


########################################
# ../../../../omdev/interp/subprocesses.py
# ruff: noqa: UP006 UP007


DEFAULT_CMD_TRY_EXCEPTIONS: ta.AbstractSet[ta.Type[Exception]] = frozenset([
    FileNotFoundError,
])


def cmd(
        cmd: ta.Union[str, ta.Sequence[str]],
        *,
        try_: ta.Union[bool, ta.Iterable[ta.Type[Exception]]] = False,
        env: ta.Optional[ta.Mapping[str, str]] = None,
        **kwargs,
) -> ta.Optional[str]:
    log.debug(cmd)
    if env:
        log.debug(env)

    env = {**os.environ, **(env or {})}

    es: tuple[ta.Type[Exception], ...] = (Exception,)
    if isinstance(try_, bool):
        if try_:
            es = tuple(DEFAULT_CMD_TRY_EXCEPTIONS)
    elif try_:
        es = tuple(try_)
        try_ = True

    try:
        buf = subprocess_check_output(*cmd, env=env, **kwargs)
    except es:
        if try_:
            log.exception('cmd failed: %r', cmd)
            return None
        else:
            raise

    out = buf.decode('utf-8').strip()
    log.debug(out)
    return out


########################################
# ../base.py
# ruff: noqa: UP006


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
# ../../../../omdev/interp/resolvers/base.py
# ruff: noqa: UP007


class InterpResolver:

    def __init__(
            self,
            version: str,
            *,
            debug: bool = False,
            include_current_python: bool = False,
    ) -> None:
        if version is not None and not (isinstance(version, str) and version.strip()):
            raise ValueError(f'version: {version!r}')
        if not isinstance(debug, bool):
            raise TypeError(f'debug: {debug!r}')

        super().__init__()

        self._version = version.strip()
        self._debug = debug
        self._include_current_python = include_current_python

    def _get_python_ver(self, bin_path: str) -> ta.Optional[str]:
        s = cmd([bin_path, '--version'], try_=True)
        if s is None:
            return None
        ps = s.strip().splitlines()[0].split()
        if ps[0] != 'Python':
            return None
        return ps[1]

    def _resolve_which_python(self) -> ta.Optional[str]:
        wp = shutil.which('python3')
        if wp is None:
            return None
        wpv = self._get_python_ver(wp)
        if wpv == self._version:
            return wp
        return None

    def _resolve_current_python(self) -> ta.Optional[str]:
        if sys.version.split()[0] == self._version:
            return sys.executable
        return None

    def _resolvers(self) -> ta.Sequence[ta.Callable[[], ta.Optional[str]]]:
        return [
            self._resolve_which_python,
            *((self._resolve_current_python,) if self._include_current_python else ()),
        ]

    def resolve(self) -> ta.Optional[str]:
        for fn in self._resolvers():
            p = fn()
            if p is not None:
                return p
        return None


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
# ../../../../omdev/interp/resolvers/pyenv.py
# ruff: noqa: UP007


class PyenvInstallOpts(ta.NamedTuple):
    opts: ta.Sequence[str]
    conf_opts: ta.Sequence[str]
    cflags: ta.Sequence[str]
    ldflags: ta.Sequence[str]
    env: ta.Mapping[str, str]

    @classmethod
    def new(
            cls,
            *,
            opts: ta.Optional[ta.Sequence[str]] = None,
            conf_opts: ta.Optional[ta.Sequence[str]] = None,
            cflags: ta.Optional[ta.Sequence[str]] = None,
            ldflags: ta.Optional[ta.Sequence[str]] = None,
            env: ta.Optional[ta.Mapping[str, str]] = None,
    ) -> 'PyenvInstallOpts':
        return cls(
            opts=opts if opts is not None else [],
            conf_opts=conf_opts if conf_opts is not None else [],
            cflags=cflags if cflags is not None else [],
            ldflags=ldflags if ldflags is not None else [],
            env=env if env is not None else {},
        )

    def combine(self, *others: 'PyenvInstallOpts') -> 'PyenvInstallOpts':
        opts = [*self.opts]
        conf_opts = [*self.conf_opts]
        cflags = [*self.cflags]
        ldflags = [*self.ldflags]
        env = {**self.env}

        for other in others:
            opts.extend(other.opts)
            conf_opts.extend(other.conf_opts)
            cflags.extend(other.cflags)
            ldflags.extend(other.ldflags)
            env.update(other.env)

        return PyenvInstallOpts(
            opts=opts,
            conf_opts=conf_opts,
            cflags=cflags,
            ldflags=ldflags,
            env=env,
        )


class PyenvInterpResolver(InterpResolver):

    def __init__(
            self,
            *args,
            pyenv_root: ta.Optional[str] = None,
            **kwargs,
    ) -> None:
        if pyenv_root is not None and not (isinstance(pyenv_root, str) and pyenv_root):
            raise ValueError(f'pyenv_root: {pyenv_root!r}')

        super().__init__(*args, **kwargs)

        self._pyenv_root_kw = pyenv_root

    @cached_nullary
    def _pyenv_root(self) -> ta.Optional[str]:
        if self._pyenv_root_kw is not None:
            return self._pyenv_root_kw

        if shutil.which('pyenv'):
            return cmd(['pyenv', 'root'])

        d = os.path.expanduser('~/.pyenv')
        if os.path.isdir(d) and os.path.isfile(os.path.join(d, 'bin', 'pyenv')):
            return d

        return None

    @cached_nullary
    def _pyenv_bin(self) -> str:
        return os.path.join(check_not_none(self._pyenv_root()), 'bin', 'pyenv')

    @cached_nullary
    def _pyenv_install_name(self) -> str:
        return self._version + ('-debug' if self._debug else '')

    @cached_nullary
    def _pyenv_install_path(self) -> str:
        return str(os.path.join(check_not_none(self._pyenv_root()), 'versions', self._pyenv_install_name()))

    @cached_nullary
    def _pyenv_basic_pio(self) -> PyenvInstallOpts:
        return PyenvInstallOpts.new(opts=['-s', '-v'])

    @cached_nullary
    def _pyenv_debug_pio(self) -> PyenvInstallOpts:
        if not self._debug:
            return PyenvInstallOpts.new()
        return PyenvInstallOpts.new(opts=['-g'])

    def _pyenv_pios(self) -> ta.Sequence[PyenvInstallOpts]:
        return [
            self._pyenv_basic_pio(),
            self._pyenv_debug_pio(),
        ]

    def _resolve_pyenv_existing_python(self) -> ta.Optional[str]:
        bin_path = os.path.join(self._pyenv_install_path(), 'bin', 'python')
        if os.path.isfile(bin_path):
            return bin_path
        return None

    def _resolve_pyenv_install_python(self) -> ta.Optional[str]:
        pio = PyenvInstallOpts.new().combine(*self._pyenv_pios())

        env = dict(pio.env)
        for k, l in [
            ('CFLAGS', pio.cflags),
            ('LDFLAGS', pio.ldflags),
            ('PYTHON_CONFIGURE_OPTS', pio.conf_opts),
        ]:
            v = ' '.join(l)
            if k in os.environ:
                v += ' ' + os.environ[k]
            env[k] = v

        cmd([self._pyenv_bin(), 'install', *pio.opts, self._version], env=env)

        bin_path = os.path.join(self._pyenv_install_path(), 'bin', 'python')
        if not os.path.isfile(bin_path):
            raise RuntimeError(f'Interpreter not found: {bin_path}')
        return bin_path

    def _resolvers(self) -> ta.Sequence[ta.Callable[[], ta.Optional[str]]]:
        return [
            *super()._resolvers(),
            self._resolve_pyenv_existing_python,
            self._resolve_pyenv_install_python,
        ]


########################################
# ../../../../omdev/interp/resolvers/linux.py


class LinuxInterpResolver(PyenvInterpResolver):

    def _pyenv_pios(self) -> ta.Sequence[PyenvInstallOpts]:
        return [
            *super()._pyenv_pios(),
        ]


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
    cfg = unmarshal_obj(dct, DeployConfig)
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
