# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import typing as ta


T = ta.TypeVar('T')
ConcernT = ta.TypeVar('ConcernT')
ConfigT = ta.TypeVar('ConfigT')


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
    Config: ta.ClassVar[type]
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
SiteConcernConfigT = ta.TypeVar('SiteConcernConfigT', bound='SiteConcern.Config')


class SiteConcern(abc.ABC, ta.Generic[SiteConcernConfigT]):
    @dc.dataclass(frozen=True)
    class Config(abc.ABC):  # noqa
        pass

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


class Site(ConcernsContainer[SiteConcern, 'Site.Config']):
    @dc.dataclass(frozen=True)
    class Config:
        user = 'omlish'

        root_dir: str = '~/deploy'

        concerns: ta.List[SiteConcern.Config] = dc.field(default_factory=list)

    @abc.abstractmethod
    def run(self, runtime: Runtime) -> None:
        raise NotImplementedError


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
    def run(self, runtime: Runtime) -> None:
        raise NotImplementedError


##


class Deploy(ConcernsContainer[DeployConcern, 'Deploy.Config']):
    @dc.dataclass(frozen=True)
    class Config:
        site: Site.Config

        name: str

        concerns: ta.List[DeployConcern.Config] = dc.field(default_factory=list)

    @property
    @abc.abstractmethod
    def site(self) -> Site:
        raise NotImplementedError

    @abc.abstractmethod
    def run(self, runtime: Runtime) -> None:
        raise NotImplementedError
