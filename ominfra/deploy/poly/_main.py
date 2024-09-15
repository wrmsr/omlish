#!/usr/bin/env python3
# noinspection DuplicatedCode
# @omlish-lite
# @omlish-script
# @omdev-amalg-output main.py
# ruff: noqa: N802 UP006 UP007 UP036
import abc
import dataclasses as dc
import datetime
import functools
import inspect
import json
import logging
import os
import os.path
import shlex
import stat
import subprocess
import sys
import textwrap
import threading
import typing as ta


########################################


if sys.version_info < (3, 8):
    raise OSError(
        f'Requires python (3, 8), got {sys.version_info} from {sys.executable}')  # noqa


########################################


# ../base.py
T = ta.TypeVar('T')
ConcernT = ta.TypeVar('ConcernT')
ConfigT = ta.TypeVar('ConfigT')
SiteConcernConfigT = ta.TypeVar('SiteConcernConfigT', bound='SiteConcernConfig')
DeployConcernConfigT = ta.TypeVar('DeployConcernConfigT', bound='DeployConcernConfig')


########################################
# ../configs.py


##


@dc.dataclass(frozen=True)
class SiteConcernConfig(abc.ABC):  # noqa
    pass


@dc.dataclass(frozen=True)
class SiteConfig:
    user = 'omlish'

    root_dir: str = '~/deploy'

    concerns: ta.List[SiteConcernConfig] = dc.field(default_factory=list)


##


@dc.dataclass(frozen=True)
class DeployConcernConfig(abc.ABC):  # noqa
    pass


@dc.dataclass(frozen=True)
class DeployConfig:
    site: SiteConfig

    name: str

    concerns: ta.List[DeployConcernConfig] = dc.field(default_factory=list)


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
# ../base.py


##


@dc.dataclass(frozen=True)
class FsItem(abc.ABC):
    path: str

    @property
    @abc.abstractmethod
    def is_dir(self) -> bool:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class FsFile(FsItem):
    @property
    def is_dir(self) -> bool:
        return False


@dc.dataclass(frozen=True)
class FsDir(FsItem):
    @property
    def is_dir(self) -> bool:
        return True


##


class Runtime(abc.ABC):
    class Stat(ta.NamedTuple):
        path: str
        is_dir: bool

    @abc.abstractmethod
    def stat(self, p: str) -> ta.Optional[Stat]:
        raise NotImplementedError

    @abc.abstractmethod
    def make_dirs(self, p: str, exist_ok: bool = False) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def write_file(self, p: str, c: ta.Union[str, bytes]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def sh(self, *ss: str) -> None:
        raise NotImplementedError


##


class ConcernsContainer(abc.ABC, ta.Generic[ConcernT, ConfigT]):
    concern_cls: ta.ClassVar[type]

    def __init__(
            self,
            config: ConfigT,
    ) -> None:
        super().__init__()
        self._config = config

        concern_cls_dct = self._concern_cls_by_config_cls()
        self._concerns = [
            concern_cls_dct[type(c)](c, self)  # type: ignore
            for c in config.concerns  # type: ignore
        ]
        self._concerns_by_cls: ta.Dict[ta.Type[ConcernT], ConcernT] = {}
        for c in self._concerns:
            if type(c) in self._concerns_by_cls:
                raise TypeError(f'Duplicate concern type: {c}')
            self._concerns_by_cls[type(c)] = c

    @classmethod
    def _concern_cls_by_config_cls(cls) -> ta.Mapping[type, ta.Type[ConcernT]]:
        return {  # noqa
            c.Config: c  # type: ignore
            for c in cls.concern_cls.__subclasses__()
        }

    @property
    def config(self) -> ConfigT:
        return self._config

    @property
    def concerns(self) -> ta.List[ConcernT]:
        return self._concerns

    def concern(self, cls: ta.Type[T]) -> T:
        return self._concerns_by_cls[cls]  # type: ignore


##


SiteConcernT = ta.TypeVar('SiteConcernT', bound='SiteConcern')


class SiteConcern(abc.ABC, ta.Generic[SiteConcernConfigT]):
    def __init__(self, config: SiteConcernConfigT, site: 'Site') -> None:
        super().__init__()
        self._config = config
        self._site = site

    @property
    def config(self) -> SiteConcernConfigT:
        return self._config

    @abc.abstractmethod
    def run(self, runtime: Runtime) -> None:
        raise NotImplementedError


##


class Site(ConcernsContainer[SiteConcern, SiteConfig]):
    @abc.abstractmethod
    def run(self, runtime: Runtime) -> None:
        raise NotImplementedError


##


DeployConcernT = ta.TypeVar('DeployConcernT', bound='DeployConcern')


class DeployConcern(abc.ABC, ta.Generic[DeployConcernConfigT]):
    def __init__(self, config: DeployConcernConfigT, deploy: 'Deploy') -> None:
        super().__init__()
        self._config = config
        self._deploy = deploy

    @property
    def config(self) -> DeployConcernConfigT:
        return self._config

    def fs_items(self) -> ta.Sequence[FsItem]:
        return []

    @abc.abstractmethod
    def run(self, runtime: Runtime) -> None:
        raise NotImplementedError


##


class Deploy(ConcernsContainer[DeployConcern, DeployConfig]):
    @property
    @abc.abstractmethod
    def site(self) -> Site:
        raise NotImplementedError

    @abc.abstractmethod
    def run(self, runtime: Runtime) -> None:
        raise NotImplementedError


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
# ../deploy.py


class DeployImpl(Deploy):
    concern_cls = DeployConcern

    def __init__(
            self,
            config: DeployConfig,
            site: Site,
    ) -> None:
        super().__init__(config)
        self._site = site

    @property
    def site(self) -> Site:
        return self._site

    def run(self, runtime: Runtime) -> None:
        for c in self._concerns:
            c.run(runtime)


########################################
# ../nginx.py


class NginxSiteConcern(SiteConcern['NginxSiteConcern.Config']):
    @dc.dataclass(frozen=True)
    class Config(SiteConcernConfig):
        global_conf_file: str = '/etc/nginx/sites-enabled/omlish.conf'

    @cached_nullary
    def confs_dir(self) -> str:
        return os.path.join(self._site.config.root_dir, 'conf', 'nginx')

    def run(self, runtime: Runtime) -> None:
        if runtime.stat(self._config.global_conf_file) is None:
            runtime.write_file(
                self._config.global_conf_file,
                f'include {self.confs_dir()}/*.conf;\n',
            )


class NginxDeployConcern(DeployConcern['NginxDeployConcern.Config']):
    @dc.dataclass(frozen=True)
    class Config(DeployConcernConfig):
        listen_port: int = 80
        proxy_port: int = 8000

    @cached_nullary
    def conf_file(self) -> str:
        return os.path.join(self._deploy.site.concern(NginxSiteConcern).confs_dir(), self._deploy.config.name + '.conf')

    @cached_nullary
    def fs_items(self) -> ta.Sequence[FsItem]:
        return [FsFile(self.conf_file())]

    def run(self, runtime: Runtime) -> None:
        runtime.make_dirs(os.path.dirname(self.conf_file()))

        conf = textwrap.dedent(f"""
            server {{
                listen {self._config.listen_port};
                location / {{
                    proxy_pass http://127.0.0.1:{self._config.proxy_port}/;
                }}
            }}
        """)

        runtime.write_file(self.conf_file(), conf)


########################################
# ../repo.py


class RepoDeployConcern(DeployConcern['RepoDeployConcern.Config']):
    @dc.dataclass(frozen=True)
    class Config(DeployConcernConfig):
        url: str
        revision: str = 'master'
        init_submodules: bool = False

    @cached_nullary
    def repo_dir(self) -> str:
        return os.path.join(self._deploy.site.config.root_dir, 'repos', self._deploy.config.name)

    @cached_nullary
    def fs_items(self) -> ta.Sequence[FsItem]:
        return [FsDir(self.repo_dir())]

    def run(self, runtime: Runtime) -> None:
        runtime.make_dirs(self.repo_dir())

        runtime.sh(
            f'cd {self.repo_dir()}',
            'git init',
            f'git remote add origin {self._config.url}',
            f'git fetch --depth 1 origin {self._config.revision}',
            'git checkout FETCH_HEAD',
            *([
                'git submodule update --init',
            ] if self._config.init_submodules else []),
        )


########################################
# ../site.py


class SiteImpl(Site):
    concern_cls = SiteConcern

    def run(self, runtime: Runtime) -> None:
        for c in self._concerns:
            c.run(runtime)


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
# ../runtime.py


class RuntimeImpl(Runtime):
    def __init__(self) -> None:
        super().__init__()

    def stat(self, p: str) -> ta.Optional[Runtime.Stat]:
        try:
            st = os.stat(p)
        except FileNotFoundError:
            return None
        else:
            return Runtime.Stat(
                path=p,
                is_dir=bool(st.st_mode & stat.S_IFDIR),
            )

    def make_dirs(self, p: str, exist_ok: bool = False) -> None:
        os.makedirs(p, exist_ok=exist_ok)

    def write_file(self, p: str, c: ta.Union[str, bytes]) -> None:
        if os.path.exists(p):
            raise RuntimeError(f'Path exists: {p}')
        with open(p, 'w' if isinstance(c, str) else 'wb') as f:
            f.write(c)

    def sh(self, *ss: str) -> None:
        s = ' && '.join(ss)
        log.info('Executing: %s', s)
        subprocess_check_call(s, shell=True)


########################################
# ../venv.py


class VenvDeployConcern(DeployConcern['VenvDeployConcern.Config']):
    @dc.dataclass(frozen=True)
    class Config(DeployConcernConfig):
        interp_version: str
        requirements_txt: str = 'requirements.txt'

    @cached_nullary
    def venv_dir(self) -> str:
        return os.path.join(self._deploy.site.config.root_dir, 'venvs', self._deploy.config.name)

    @cached_nullary
    def fs_items(self) -> ta.Sequence[FsItem]:
        return [FsDir(self.venv_dir())]

    @cached_nullary
    def exe(self) -> str:
        return os.path.join(self.venv_dir(), 'bin', 'python')

    def run(self, runtime: Runtime) -> None:
        runtime.make_dirs(self.venv_dir())

        rd = self._deploy.concern(RepoDeployConcern).repo_dir()

        l, r = os.path.split(self.venv_dir())

        # FIXME: lol
        py_exe = 'python3'

        runtime.sh(
            f'cd {l}',
            f'{py_exe} -mvenv {r}',

            # https://stackoverflow.com/questions/77364550/attributeerror-module-pkgutil-has-no-attribute-impimporter-did-you-mean
            f'{self.exe()} -m ensurepip',
            f'{self.exe()} -mpip install --upgrade setuptools pip',

            f'{self.exe()} -mpip install -r {rd}/{self._config.requirements_txt}',  # noqa
        )


########################################
# ../supervisor.py


# class SupervisorSiteConcern(SiteConcern['SupervisorSiteConcern.Config']):
#     @dc.dataclass(frozen=True)
#     class Config(DeployConcern.Config):
#         global_conf_file: str = '/etc/supervisor/conf.d/supervisord.conf'
#
#     def run(self) -> None:
#         sup_conf_dir = os.path.join(self._d.home_dir(), 'conf/supervisor')
#         with open(self._d.host_cfg.global_supervisor_conf_file_path) as f:
#             glo_sup_conf = f.read()
#         if sup_conf_dir not in glo_sup_conf:
#             log.info('Updating global supervisor conf at %s', self._d.host_cfg.global_supervisor_conf_file_path)  # noqa
#             glo_sup_conf += textwrap.dedent(f"""
#                 [include]
#                 files = {self._d.home_dir()}/conf/supervisor/*.conf
#             """)
#             with open(self._d.host_cfg.global_supervisor_conf_file_path, 'w') as f:
#                 f.write(glo_sup_conf)


class SupervisorDeployConcern(DeployConcern['SupervisorDeployConcern.Config']):
    @dc.dataclass(frozen=True)
    class Config(DeployConcernConfig):
        entrypoint: str

    @cached_nullary
    def conf_file(self) -> str:
        return os.path.join(self._deploy.site.config.root_dir, 'conf', 'supervisor', self._deploy.config.name + '.conf')

    @cached_nullary
    def fs_items(self) -> ta.Sequence[FsItem]:
        return [FsFile(self.conf_file())]

    def run(self, runtime: Runtime) -> None:
        runtime.make_dirs(os.path.dirname(self.conf_file()))

        rd = self._deploy.concern(RepoDeployConcern).repo_dir()
        vx = self._deploy.concern(VenvDeployConcern).exe()

        conf = textwrap.dedent(f"""
            [program:{self._deploy.config.name}]
            command={vx} -m {self._config.entrypoint}
            directory={rd}
            user={self._deploy.site.config.user}
            autostart=true
            autorestart=true
        """)

        runtime.write_file(self.conf_file(), conf)


########################################
# main.py


def _main() -> None:
    pass


if __name__ == '__main__':
    _main()
