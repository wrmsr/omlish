# ruff: noqa: UP006 UP007
"""
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

==

for dn in [
    'app',
    'conf',
    'conf/env',
    'conf/nginx',
    'conf/supervisor',
    'venv',
]:
"""
import abc
import dataclasses as dc
import os.path
import typing as ta

from omlish.lite.check import check_equal
from omlish.lite.check import check_non_empty


DeployPathKind = ta.Literal['dir', 'file']  # ta.TypeAlias


##


DEPLOY_PATH_SPEC_PLACEHOLDER = '@'



@dc.dataclass(frozen=True)
class DeployPathPart(abc.ABC):  # noqa
    @property
    @abc.abstractmethod
    def kind(self) -> DeployPathKind:
        raise NotImplementedError

    @abc.abstractmethod
    def render(self) -> str:
        raise NotImplementedError


class DeployPathDir(DeployPathPart, abc.ABC):
    @property
    def kind(self) -> DeployPathKind:
        return 'dir'

    @classmethod
    def parse(cls, s: str) -> 'DeployPathDir':
        raise NotImplementedError


class DeployPathFile(DeployPathPart, abc.ABC):
    @property
    def kind(self) -> DeployPathKind:
        return 'file'

    @classmethod
    def parse(cls, s: str) -> 'DeployPathFile':
        raise NotImplementedError


@dc.dataclass(frozen=True)
class ConstDeployPathPart(DeployPathPart, abc.ABC):
    name: str

    def render(self) -> str:
        return self.name


class DeployConstDir(ConstDeployPathPart, DeployPathDir):
    pass


class DeployConstFile(ConstDeployPathPart, DeployPathFile):
    pass


class DeploySpecDir(DeployPathPart, DeployPathDir):
    def render(self) -> str:
        return DEPLOY_PATH_SPEC_PLACEHOLDER


@dc.dataclass(frozen=True)
class DeploySpecFile(DeployPathPart, DeployPathFile):
    suffix: ta.Optional[str] = None

    def render(self) -> str:
        return DEPLOY_PATH_SPEC_PLACEHOLDER + self.suffix


@dc.dataclass(frozen=True)
class DeployPath:
    parts: ta.Sequence[DeployPathPart]

    def __post_init__(self) -> None:
        check_non_empty(self.parts)
        for p in self.parts[:-1]:
            check_equal(p.kind, 'dir')

    @property
    def kind(self) -> ta.Literal['file', 'dir']:
        return self.parts[-1].kind

    def render(self) -> str:
        return os.path.join(*[p.render() for p in self.parts])  # noqa

    @classmethod
    def parse(cls, s: str) -> 'DeployPath':
        raise NotImplementedError
