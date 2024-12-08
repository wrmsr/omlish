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
from omlish.lite.check import check_non_empty_str
from omlish.lite.check import check_not_in


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


#


class DeployPathDir(DeployPathPart, abc.ABC):
    @property
    def kind(self) -> DeployPathKind:
        return 'dir'

    @classmethod
    def parse(cls, s: str) -> 'DeployPathDir':
        if DEPLOY_PATH_SPEC_PLACEHOLDER in s:
            check_equal(s, DEPLOY_PATH_SPEC_PLACEHOLDER)
            return SpecDeployPathDir()
        else:
            return ConstDeployPathDir(s)


class DeployPathFile(DeployPathPart, abc.ABC):
    @property
    def kind(self) -> DeployPathKind:
        return 'file'

    @classmethod
    def parse(cls, s: str) -> 'DeployPathFile':
        if DEPLOY_PATH_SPEC_PLACEHOLDER in s:
            check_equal(s[0], DEPLOY_PATH_SPEC_PLACEHOLDER)
            return SpecDeployPathFile(s[1:])
        else:
            return ConstDeployPathFile(s)


#


@dc.dataclass(frozen=True)
class ConstDeployPathPart(DeployPathPart, abc.ABC):
    name: str

    def __post_init__(self) -> None:
        check_non_empty_str(self.name)
        check_not_in('/', self.name)
        check_not_in(DEPLOY_PATH_SPEC_PLACEHOLDER, self.name)

    def render(self) -> str:
        return self.name


class ConstDeployPathDir(ConstDeployPathPart, DeployPathDir):
    pass


class ConstDeployPathFile(ConstDeployPathPart, DeployPathFile):
    pass


#


class SpecDeployPathPart(DeployPathPart, abc.ABC):
    pass


class SpecDeployPathDir(SpecDeployPathPart, DeployPathDir):
    def render(self) -> str:
        return DEPLOY_PATH_SPEC_PLACEHOLDER


@dc.dataclass(frozen=True)
class SpecDeployPathFile(SpecDeployPathPart, DeployPathFile):
    suffix: str

    def __post_init__(self) -> None:
        check_non_empty_str(self.suffix)
        check_not_in('/', self.suffix)
        check_not_in(DEPLOY_PATH_SPEC_PLACEHOLDER, self.suffix)

    def render(self) -> str:
        return DEPLOY_PATH_SPEC_PLACEHOLDER + self.suffix


##


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
        return os.path.join(  # noqa
            *[p.render() for p in self.parts],
            *([''] if self.kind == 'dir' else []),
        )

    @classmethod
    def parse(cls, s: str) -> 'DeployPath':
        tail_parse: ta.Callable[[str], DeployPathPart]
        if s.endswith('/'):
            tail_parse = DeployPathDir.parse
            s = s[:-1]
        else:
            tail_parse = DeployPathFile.parse
        ps = check_non_empty_str(s).split('/')
        return cls([
            *([DeployPathDir.parse(p) for p in ps[:-1]] if len(ps) > 1 else []),
            tail_parse(ps[-1]),
        ])
