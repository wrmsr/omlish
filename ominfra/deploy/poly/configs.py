# ruff: noqa: UP006
import abc
import dataclasses as dc
import typing as ta


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
