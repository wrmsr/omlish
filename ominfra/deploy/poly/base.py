# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import typing as ta


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
DeployConcernConfigT = ta.TypeVar('DeployConcernConfigT', bound='DeployConcern.Config')


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
