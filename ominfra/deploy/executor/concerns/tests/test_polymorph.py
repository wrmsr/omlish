# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import json
import os.path
import tempfile
import typing as ta
import unittest

from omlish.lite.cached import cached_nullary
from omlish.lite.json import json_dumps_compact
from omlish.lite.logs import configure_standard_logging  # noqa
from omlish.lite.logs import log
from omlish.lite.marshal import marshal_obj
from omlish.lite.marshal import unmarshal_obj
from omlish.lite.runtime import is_debugger_attached
from omlish.lite.subprocesses import subprocess_check_call


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


ConcernT = ta.TypeVar('ConcernT', bound='Concern')
ConcernConfigT = ta.TypeVar('ConcernConfigT', bound='Concern.Config')


class Concern(abc.ABC, ta.Generic[ConcernConfigT]):
    @dc.dataclass(frozen=True)
    class Config(abc.ABC):  # noqa
        pass

    def __init__(self, config: ConcernConfigT, deploy: 'Deploy') -> None:
        super().__init__()
        self._config = config
        self._deploy = deploy

    @property
    def config(self) -> ConcernConfigT:
        return self._config

    def fs_items(self) -> ta.Sequence[FsItem]:
        return []

    @abc.abstractmethod
    def run(self) -> None:
        raise NotImplementedError


##


class RepoConcern(Concern['RepoConcern.Config']):
    @dc.dataclass(frozen=True)
    class Config(Concern.Config):
        url: str
        revision: ta.Optional[str] = None
        init_submodules: bool = False

    @cached_nullary
    def repo_dir(self) -> str:
        return os.path.join(self._deploy.config.root_dir, 'repos', self._deploy.config.name)

    @cached_nullary
    def fs_items(self) -> ta.Sequence[FsItem]:
        return [FsDir(self.repo_dir())]

    def run(self) -> None:
        rd = self.repo_dir()
        self._deploy.runtime().makedirs(rd)
        l, r = os.path.split(rd)

        self._deploy.runtime().sh(
            f'cd {l}',
            f'git clone --depth 1 {self._config.url} {r}',
            *([
                f'cd {r}',
                'git submodule update --init',
            ] if self._config.init_submodules else []),
        )


##


class VenvConcern(Concern['VenvConcern.Config']):
    @dc.dataclass(frozen=True)
    class Config(Concern.Config):
        interp_version: str
        requirements_txt: str = 'requirements.txt'

    @cached_nullary
    def venv_dir(self) -> str:
        return os.path.join(self._deploy.config.root_dir, 'venvs', self._deploy.config.name)

    @cached_nullary
    def fs_items(self) -> ta.Sequence[FsItem]:
        return [FsDir(self.venv_dir())]

    def run(self) -> None:
        rd = self._deploy.concern(RepoConcern).repo_dir()

        vd = self.venv_dir()
        self._deploy.runtime().makedirs(vd)
        l, r = os.path.split(vd)

        py_exe = 'python3'

        self._deploy.runtime().sh(
            f'cd {l}',
            f'{py_exe} -mvenv {r}',

            # https://stackoverflow.com/questions/77364550/attributeerror-module-pkgutil-has-no-attribute-impimporter-did-you-mean
            f'{vd}/bin/python -m ensurepip',
            f'{vd}/bin/python -mpip install --upgrade setuptools pip',

            f'{vd}/bin/python -mpip install -r {rd}/{self._config.requirements_txt}',  # noqa
        )


##


class DeployRuntime:
    def __init__(self, deploy: 'Deploy') -> None:
        super().__init__()
        self._deploy = deploy

    def makedirs(self, p: str, exist_ok: bool = False) -> None:
        os.makedirs(p, exist_ok=exist_ok)

    def sh(self, *ss: str) -> None:
        s = ' && '.join(ss)
        log.info('Executing: %s', s)
        subprocess_check_call(s, shell=True)


##


CONCERN_CLS_BY_CONFIG_CLS: ta.Mapping[ta.Type[Concern.Config], ta.Type[Concern]] = {
    cls.Config: cls  # type: ignore
    for cls in Concern.__subclasses__()
}


class Deploy:
    @dc.dataclass(frozen=True)
    class Config:
        name: str

        root_dir: str = '~/deploy'

        concerns: ta.List[Concern.Config] = dc.field(default_factory=list)

    def __init__(
            self,
            config: Config,
            runtime_cls: ta.Optional[ta.Type[DeployRuntime]] = None,
    ) -> None:
        super().__init__()
        self._config = config

        self._concerns = [
            CONCERN_CLS_BY_CONFIG_CLS[type(c)](c, self)
            for c in config.concerns
        ]
        self._concerns_by_cls: ta.Dict[ta.Type[Concern], Concern] = {}
        for c in self._concerns:
            if type(c) in self._concerns_by_cls:
                raise TypeError(f'Duplicate concern type: {c}')
            self._concerns_by_cls[type(c)] = c

        runtime: ta.Optional[DeployRuntime]
        if runtime_cls is not None:
            runtime = runtime_cls(self)
        else:
            runtime = None
        self._runtime = runtime

    @property
    def config(self) -> 'Deploy.Config':
        return self._config

    @property
    def concerns(self) -> ta.List[Concern]:
        return self._concerns

    def concern(self, cls: ta.Type[ConcernT]) -> ConcernT:
        return self._concerns_by_cls[cls]  # type: ignore

    def runtime(self) -> DeployRuntime:
        if (runtime := self._runtime) is None:
            raise RuntimeError('No runtime present')
        return runtime

    def run(self) -> None:
        for c in self._concerns:
            c.run()


##


class TestPolymorph(unittest.TestCase):
    def test_polymorph(self):
        if not is_debugger_attached():
            self.skipTest('debugger only')

        configure_standard_logging('DEBUG')

        print()

        root_dir = tempfile.mkdtemp('-ominfra-deploy-polymorph-test')
        print(root_dir)

        dcfg = Deploy.Config(
            name='omlish',
            root_dir=root_dir,
            concerns=[
                RepoConcern.Config(
                    url='https://github.com/wrmsr/omlish',
                ),
                VenvConcern.Config(
                    interp_version='3.12.5',
                ),
            ],
        )
        print(dcfg)

        jdcfg = json_dumps_compact(marshal_obj(dcfg))
        print(jdcfg)

        dcfg2: Deploy.Config = unmarshal_obj(json.loads(jdcfg), Deploy.Config)
        print(dcfg2)

        d = Deploy(dcfg2)
        print(d)

        d.run()
