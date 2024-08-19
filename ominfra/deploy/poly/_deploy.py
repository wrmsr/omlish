# noinspection DuplicatedCode
# @omdev-amalg-output deploy.py
# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import functools
import inspect
import logging
import os
import os.path
import shlex
import subprocess
import sys
import textwrap
import typing as ta


DeployConcernConfigT = ta.TypeVar('DeployConcernConfigT', bound='DeployConcern.Config')


########################################
# ../base.py
# ruff: noqa: UP006 UP007


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


DeployConcernT = ta.TypeVar('DeployConcernT', bound='DeployConcern')


class DeployConcern(abc.ABC, ta.Generic[DeployConcernConfigT]):
    @dc.dataclass(frozen=True)
    class Config(abc.ABC):  # noqa
        pass

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
    def run(self) -> None:
        raise NotImplementedError


##


class DeployRuntime(abc.ABC):
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


class Deploy(abc.ABC):
    @dc.dataclass(frozen=True)
    class Config:
        name: str

        root_dir: str = '~/deploy'

        concerns: ta.List[DeployConcern.Config] = dc.field(default_factory=list)

    @property
    @abc.abstractmethod
    def config(self) -> 'Deploy.Config':
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def concerns(self) -> ta.List[DeployConcern]:
        raise NotImplementedError

    def concern(self, cls: ta.Type[DeployConcernT]) -> DeployConcernT:
        raise NotImplementedError

    def runtime(self) -> DeployRuntime:
        raise NotImplementedError

    def run(self) -> None:
        raise NotImplementedError


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
# ../../../../omlish/lite/logs.py
"""
TODO:
 - debug
"""
# ruff: noqa: UP007


log = logging.getLogger(__name__)


def configure_standard_logging(level: ta.Union[int, str] = logging.INFO) -> None:
    logging.root.addHandler(logging.StreamHandler())
    logging.root.setLevel(level)


########################################
# ../nginx.py


class NginxDeployConcern(DeployConcern['NginxDeployConcern.Config']):
    @dc.dataclass(frozen=True)
    class Config(DeployConcern.Config):
        listen_port: int = 80
        proxy_port: int = 8000

    @cached_nullary
    def conf_file(self) -> str:
        return os.path.join(self._deploy.config.root_dir, 'conf', 'nginx', self._deploy.config.name + '.conf')

    @cached_nullary
    def fs_items(self) -> ta.Sequence[FsItem]:
        return [FsFile(self.conf_file())]

    def run(self) -> None:
        self._deploy.runtime().make_dirs(os.path.dirname(self.conf_file()))

        conf = textwrap.dedent(f"""
            server {{
                listen {self._config.listen_port};
                location / {{
                    proxy_pass http://127.0.0.1:{self._config.proxy_port}/;
                }}
            }}
        """)

        self._deploy.runtime().write_file(self.conf_file(), conf)


########################################
# ../repo.py


class RepoDeployConcern(DeployConcern['RepoDeployConcern.Config']):
    @dc.dataclass(frozen=True)
    class Config(DeployConcern.Config):
        url: str
        revision: str = 'master'
        init_submodules: bool = False

    @cached_nullary
    def repo_dir(self) -> str:
        return os.path.join(self._deploy.config.root_dir, 'repos', self._deploy.config.name)

    @cached_nullary
    def fs_items(self) -> ta.Sequence[FsItem]:
        return [FsDir(self.repo_dir())]

    def run(self) -> None:
        rd = self.repo_dir()
        self._deploy.runtime().make_dirs(rd)

        self._deploy.runtime().sh(
            f'cd {rd}',
            'git init',
            f'git remote add origin {self._config.url}',
            f'git fetch --depth 1 origin {self._config.revision}',
            'git checkout FETCH_HEAD',
            *([
                'git submodule update --init',
            ] if self._config.init_submodules else []),
        )


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
# ../venv.py


class VenvDeployConcern(DeployConcern['VenvDeployConcern.Config']):
    @dc.dataclass(frozen=True)
    class Config(DeployConcern.Config):
        interp_version: str
        requirements_txt: str = 'requirements.txt'

    @cached_nullary
    def venv_dir(self) -> str:
        return os.path.join(self._deploy.config.root_dir, 'venvs', self._deploy.config.name)

    @cached_nullary
    def fs_items(self) -> ta.Sequence[FsItem]:
        return [FsDir(self.venv_dir())]

    def run(self) -> None:
        rd = self._deploy.concern(RepoDeployConcern).repo_dir()

        vd = self.venv_dir()
        self._deploy.runtime().make_dirs(vd)
        l, r = os.path.split(vd)

        py_exe = 'python3'
        v_exe = os.path.join(vd, 'bin', 'python')

        self._deploy.runtime().sh(
            f'cd {l}',
            f'{py_exe} -mvenv {r}',

            # https://stackoverflow.com/questions/77364550/attributeerror-module-pkgutil-has-no-attribute-impimporter-did-you-mean
            f'{v_exe} -m ensurepip',
            f'{v_exe} -mpip install --upgrade setuptools pip',

            f'{v_exe} -mpip install -r {rd}/{self._config.requirements_txt}',  # noqa
        )


########################################
# ../../../../omlish/lite/subprocesses.py
# ruff: noqa: UP006 UP007


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
# deploy.py


class DeployRuntimeImpl(DeployRuntime):
    def __init__(self, deploy: 'Deploy') -> None:
        super().__init__()
        self._deploy = deploy

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


##


DEPLOY_CONCERN_CLS_BY_CONFIG_CLS: ta.Mapping[ta.Type[DeployConcern.Config], ta.Type[DeployConcern]] = {
    cls.Config: cls  # type: ignore
    for cls in DeployConcern.__subclasses__()
}


class DeployImpl(Deploy):
    def __init__(
            self,
            config: Deploy.Config,
            runtime_cls: ta.Optional[ta.Type[DeployRuntime]] = None,
    ) -> None:
        super().__init__()
        self._config = config

        self._concerns = [
            DEPLOY_CONCERN_CLS_BY_CONFIG_CLS[type(c)](c, self)
            for c in config.concerns
        ]
        self._concerns_by_cls: ta.Dict[ta.Type[DeployConcern], DeployConcern] = {}
        for c in self._concerns:
            if type(c) in self._concerns_by_cls:
                raise TypeError(f'Duplicate concern type: {c}')
            self._concerns_by_cls[type(c)] = c

        runtime: ta.Optional[DeployRuntime]
        if runtime_cls is not None:
            runtime = runtime_cls(self)  # type: ignore
        else:
            runtime = None
        self._runtime = runtime

    @property
    def config(self) -> 'Deploy.Config':
        return self._config

    @property
    def concerns(self) -> ta.List[DeployConcern]:
        return self._concerns

    def concern(self, cls: ta.Type[DeployConcernT]) -> DeployConcernT:
        return self._concerns_by_cls[cls]  # type: ignore

    def runtime(self) -> DeployRuntime:
        if (runtime := self._runtime) is None:
            raise RuntimeError('No runtime present')
        return runtime

    def run(self) -> None:
        for c in self._concerns:
            c.run()
