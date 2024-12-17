# ruff: noqa: UP006 UP007
"""
TODO:
 - run/{.pid,.sock}
 - logs/...
 - current symlink
 - conf/{nginx,supervisor}
 - env/?
 - apps/<app>/shared
"""
import abc
import dataclasses as dc
import os.path
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check

from .types import DeployHome


DeployPathKind = ta.Literal['dir', 'file']  # ta.TypeAlias
DeployPathPlaceholder = ta.Literal['app', 'tag', 'conf']  # ta.TypeAlias


##


DEPLOY_PATH_PLACEHOLDER_SIGIL = '@'
DEPLOY_PATH_PLACEHOLDER_SEPARATOR = '--'
DEPLOY_PATH_PLACEHOLDER_DELIMITERS: ta.AbstractSet[str] = frozenset([DEPLOY_PATH_PLACEHOLDER_SEPARATOR, '.'])

DEPLOY_PATH_PLACEHOLDERS: ta.FrozenSet[str] = frozenset([
    'app',
    'tag',
    'conf',
])


class DeployPathError(Exception):
    pass


class DeployPathRenderable(abc.ABC):
    @abc.abstractmethod
    def render(self, placeholders: ta.Optional[ta.Mapping[DeployPathPlaceholder, str]] = None) -> str:
        raise NotImplementedError


##


class DeployPathNamePart(DeployPathRenderable, abc.ABC):
    pass


@dc.dataclass(frozen=True)
class PlaceholderDeployPathNamePart(DeployPathNamePart):
    placeholder: str

    def __post_init__(self) -> None:
        check.in_(self.placeholder, DEPLOY_PATH_PLACEHOLDERS)

    def render(self, placeholders: ta.Optional[ta.Mapping[DeployPathPlaceholder, str]] = None) -> str:
        if placeholders is not None:
            return placeholders[self.placeholder]  # type: ignore
        else:
            return DEPLOY_PATH_PLACEHOLDER_SIGIL + self.placeholder


class PlaceholderSeparatorDeployPathNamePart(DeployPathNamePart):
    def render(self, placeholders: ta.Optional[ta.Mapping[DeployPathPlaceholder, str]] = None) -> str:
        return DEPLOY_PATH_PLACEHOLDER_SEPARATOR


@dc.dataclass(frozen=True)
class ConstDeployPathNamePart(DeployPathNamePart):
    const: str

    def __post_init__(self) -> None:
        check.non_empty_str(self.const)
        for c in [DEPLOY_PATH_PLACEHOLDER_SEPARATOR, DEPLOY_PATH_PLACEHOLDER_SIGIL, '/']:
            check.not_in(c, self.const)

    def render(self, placeholders: ta.Optional[ta.Mapping[DeployPathPlaceholder, str]] = None) -> str:
        return self.const


@dc.dataclass(frozen=True)
class DeployPathName(DeployPathRenderable):
    parts: ta.Sequence[DeployPathNamePart]

    def __post_init__(self) -> None:
        hash(self)
        check.not_empty(self.parts)

    def render(self, placeholders: ta.Optional[ta.Mapping[DeployPathPlaceholder, str]] = None) -> str:
        return ''.join(p.render(placeholders) for p in self.parts)

    @classmethod
    def parse(cls, s: str) -> 'DeployPathName':
        check.non_empty_str(s)
        check.not_in('/', s)

        ps = [s]
        for d in DEPLOY_PATH_PLACEHOLDER_DELIMITERS:
            ps = [p.split(d) for p in ps]

        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class DeployPathPart(DeployPathRenderable, abc.ABC):  # noqa
    name: DeployPathName

    @property
    @abc.abstractmethod
    def kind(self) -> DeployPathKind:
        raise NotImplementedError

    def render(self, placeholders: ta.Optional[ta.Mapping[DeployPathPlaceholder, str]] = None) -> str:
        return self.name.render(placeholders) + ('/' if self.kind == 'dir' else '')

    @classmethod
    def parse(cls, s: str) -> 'DeployPath':
        raise NotImplementedError


class DirDeployPathPart(DeployPathPart):
    @property
    def kind(self) -> DeployPathKind:
        return 'dir'


class FileDeployPathPart(DeployPathPart):
    @property
    def kind(self) -> DeployPathKind:
        return 'file'


#


@dc.dataclass(frozen=True)
class DeployPath:
    parts: ta.Sequence[DeployPathPart]

    @property
    def name_parts(self) -> ta.Iterator[DeployPathNamePart]:
        for p in self.parts:
            yield from p.name.parts

    def __post_init__(self) -> None:
        hash(self)
        check.not_empty(self.parts)
        for p in self.parts[:-1]:
            check.equal(p.kind, 'dir')

        pd = {}
        for i, np in enumerate(self.name_parts):
            if isinstance(np, PlaceholderDeployPathNamePart):
                if np.placeholder in pd:
                    raise DeployPathError('Duplicate placeholders in path', self)
                pd[np.placeholder] = i

        if 'tag' in pd:
            if 'app' not in pd or pd['app'] >= pd['tag']:
                raise DeployPathError('Tag placeholder in path without preceding app', self)

    @property
    def kind(self) -> ta.Literal['file', 'dir']:
        return self.parts[-1].kind

    def render(self, placeholders: ta.Optional[ta.Mapping[DeployPathPlaceholder, str]] = None) -> str:
        return '/'.join(  # noqa
            *[p.render(placeholders) for p in self.parts],
            *([''] if self.kind == 'dir' else []),
        )

    @classmethod
    def parse(cls, s: str) -> 'DeployPath':
        check.non_empty_str(s)
        ps = []
        i = 0
        while i < len(s):
            if (n := s.find('/', i)) < i:
                ps.append(s[i:])
                break
            ps.append(s[i:n + 1])
            i = n + 1

        raise NotImplementedError


##


class DeployPathOwner(abc.ABC):
    @abc.abstractmethod
    def get_owned_deploy_paths(self) -> ta.AbstractSet[DeployPath]:
        raise NotImplementedError


DeployPathOwners = ta.NewType('DeployPathOwners', ta.Sequence[DeployPathOwner])


class SingleDirDeployPathOwner(DeployPathOwner, abc.ABC):
    def __init__(
            self,
            *args: ta.Any,
            owned_dir: str,
            deploy_home: ta.Optional[DeployHome],
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        check.not_in('/', owned_dir)
        self._owned_dir: str = check.non_empty_str(owned_dir)

        self._deploy_home = deploy_home

        self._owned_deploy_paths = frozenset([DeployPath.parse(self._owned_dir + '/')])

    @cached_nullary
    def _dir(self) -> str:
        return os.path.join(check.non_empty_str(self._deploy_home), self._owned_dir)

    @cached_nullary
    def _make_dir(self) -> str:
        if not os.path.isdir(d := self._dir()):
            os.makedirs(d, exist_ok=True)
        return d

    def get_owned_deploy_paths(self) -> ta.AbstractSet[DeployPath]:
        return self._owned_deploy_paths
