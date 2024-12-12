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

==

"""
import abc
import dataclasses as dc
import os.path
import typing as ta

from omlish.lite.check import check


DeployPathKind = ta.Literal['dir', 'file']  # ta.TypeAlias
DeployPathSpec = ta.Literal['app', 'deploy']  # ta.TypeAlias


##


DEPLOY_PATH_SPEC_PLACEHOLDER = '@'
DEPLOY_PATH_SPEC_SEPARATORS = '-.'

DEPLOY_PATH_SPECS: ta.FrozenSet[str] = frozenset([
    'app',
    'deploy',
])


class DeployPathError(Exception):
    pass


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


class DirDeployPathPart(DeployPathPart, abc.ABC):
    @property
    def kind(self) -> DeployPathKind:
        return 'dir'

    @classmethod
    def parse(cls, s: str) -> 'DirDeployPathPart':
        if DEPLOY_PATH_SPEC_PLACEHOLDER in s:
            check.equal(s[0], DEPLOY_PATH_SPEC_PLACEHOLDER)
            return SpecDirDeployPathPart(s[1:])
        else:
            return ConstDirDeployPathPart(s)


class FileDeployPathPart(DeployPathPart, abc.ABC):
    @property
    def kind(self) -> DeployPathKind:
        return 'file'

    @classmethod
    def parse(cls, s: str) -> 'FileDeployPathPart':
        if DEPLOY_PATH_SPEC_PLACEHOLDER in s:
            check.equal(s[0], DEPLOY_PATH_SPEC_PLACEHOLDER)
            if not any(c in s for c in DEPLOY_PATH_SPEC_SEPARATORS):
                return SpecFileDeployPathPart(s[1:], '')
            else:
                p = min(f for c in DEPLOY_PATH_SPEC_SEPARATORS if (f := s.find(c)) > 0)
                return SpecFileDeployPathPart(s[1:p], s[p:])
        else:
            return ConstFileDeployPathPart(s)


#


@dc.dataclass(frozen=True)
class ConstDeployPathPart(DeployPathPart, abc.ABC):
    name: str

    def __post_init__(self) -> None:
        check.non_empty_str(self.name)
        check.not_in('/', self.name)
        check.not_in(DEPLOY_PATH_SPEC_PLACEHOLDER, self.name)

    def render(self) -> str:
        return self.name


class ConstDirDeployPathPart(ConstDeployPathPart, DirDeployPathPart):
    pass


class ConstFileDeployPathPart(ConstDeployPathPart, FileDeployPathPart):
    pass


#


@dc.dataclass(frozen=True)
class SpecDeployPathPart(DeployPathPart, abc.ABC):
    spec: str  # DeployPathSpec

    def __post_init__(self) -> None:
        check.non_empty_str(self.spec)
        for c in [*DEPLOY_PATH_SPEC_SEPARATORS, DEPLOY_PATH_SPEC_PLACEHOLDER, '/']:
            check.not_in(c, self.spec)
        check.in_(self.spec, DEPLOY_PATH_SPECS)


@dc.dataclass(frozen=True)
class SpecDirDeployPathPart(SpecDeployPathPart, DirDeployPathPart):
    def render(self) -> str:
        return DEPLOY_PATH_SPEC_PLACEHOLDER + self.spec


@dc.dataclass(frozen=True)
class SpecFileDeployPathPart(SpecDeployPathPart, FileDeployPathPart):
    suffix: str

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.suffix:
            for c in [DEPLOY_PATH_SPEC_PLACEHOLDER, '/']:
                check.not_in(c, self.suffix)

    def render(self) -> str:
        return DEPLOY_PATH_SPEC_PLACEHOLDER + self.spec + self.suffix


##


@dc.dataclass(frozen=True)
class DeployPath:
    parts: ta.Sequence[DeployPathPart]

    def __post_init__(self) -> None:
        check.not_empty(self.parts)
        for p in self.parts[:-1]:
            check.equal(p.kind, 'dir')

        pd = {}
        for i, p in enumerate(self.parts):
            if isinstance(p, SpecDeployPathPart):
                if p.spec in pd:
                    raise DeployPathError('Duplicate specs in path', self)
                pd[p.spec] = i

        if 'deploy' in pd:
            if 'app' not in pd or pd['app'] >= pd['deploy']:
                raise DeployPathError('Deploy specs in path without preceding app', self)

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
            tail_parse = DirDeployPathPart.parse
            s = s[:-1]
        else:
            tail_parse = FileDeployPathPart.parse
        ps = check.non_empty_str(s).split('/')
        return cls([
            *([DirDeployPathPart.parse(p) for p in ps[:-1]] if len(ps) > 1 else []),
            tail_parse(ps[-1]),
        ])
