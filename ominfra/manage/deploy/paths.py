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
DeployPathPlaceholder = ta.Literal['app', 'tag']  # ta.TypeAlias


##


DEPLOY_PATH_PLACEHOLDER_PLACEHOLDER = '@'
DEPLOY_PATH_PLACEHOLDER_SEPARATORS = '-.'

DEPLOY_PATH_PLACEHOLDERS: ta.FrozenSet[str] = frozenset([
    'app',
    'tag',
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
    def render(self, placeholders: ta.Optional[ta.Mapping[DeployPathPlaceholder, str]] = None) -> str:
        raise NotImplementedError


#


class DirDeployPathPart(DeployPathPart, abc.ABC):
    @property
    def kind(self) -> DeployPathKind:
        return 'dir'

    @classmethod
    def parse(cls, s: str) -> 'DirDeployPathPart':
        if DEPLOY_PATH_PLACEHOLDER_PLACEHOLDER in s:
            check.equal(s[0], DEPLOY_PATH_PLACEHOLDER_PLACEHOLDER)
            return PlaceholderDirDeployPathPart(s[1:])
        else:
            return ConstDirDeployPathPart(s)


class FileDeployPathPart(DeployPathPart, abc.ABC):
    @property
    def kind(self) -> DeployPathKind:
        return 'file'

    @classmethod
    def parse(cls, s: str) -> 'FileDeployPathPart':
        if DEPLOY_PATH_PLACEHOLDER_PLACEHOLDER in s:
            check.equal(s[0], DEPLOY_PATH_PLACEHOLDER_PLACEHOLDER)
            if not any(c in s for c in DEPLOY_PATH_PLACEHOLDER_SEPARATORS):
                return PlaceholderFileDeployPathPart(s[1:], '')
            else:
                p = min(f for c in DEPLOY_PATH_PLACEHOLDER_SEPARATORS if (f := s.find(c)) > 0)
                return PlaceholderFileDeployPathPart(s[1:p], s[p:])
        else:
            return ConstFileDeployPathPart(s)


#


@dc.dataclass(frozen=True)
class ConstDeployPathPart(DeployPathPart, abc.ABC):
    name: str

    def __post_init__(self) -> None:
        check.non_empty_str(self.name)
        check.not_in('/', self.name)
        check.not_in(DEPLOY_PATH_PLACEHOLDER_PLACEHOLDER, self.name)

    def render(self, placeholders: ta.Optional[ta.Mapping[DeployPathPlaceholder, str]] = None) -> str:
        return self.name


class ConstDirDeployPathPart(ConstDeployPathPart, DirDeployPathPart):
    pass


class ConstFileDeployPathPart(ConstDeployPathPart, FileDeployPathPart):
    pass


#


@dc.dataclass(frozen=True)
class PlaceholderDeployPathPart(DeployPathPart, abc.ABC):
    placeholder: str  # DeployPathPlaceholder

    def __post_init__(self) -> None:
        check.non_empty_str(self.placeholder)
        for c in [*DEPLOY_PATH_PLACEHOLDER_SEPARATORS, DEPLOY_PATH_PLACEHOLDER_PLACEHOLDER, '/']:
            check.not_in(c, self.placeholder)
        check.in_(self.placeholder, DEPLOY_PATH_PLACEHOLDERS)

    def _render_placeholder(self, placeholders: ta.Optional[ta.Mapping[DeployPathPlaceholder, str]] = None) -> str:
        if placeholders is not None:
            return placeholders[self.placeholder]  # type: ignore
        else:
            return DEPLOY_PATH_PLACEHOLDER_PLACEHOLDER + self.placeholder


@dc.dataclass(frozen=True)
class PlaceholderDirDeployPathPart(PlaceholderDeployPathPart, DirDeployPathPart):
    def render(self, placeholders: ta.Optional[ta.Mapping[DeployPathPlaceholder, str]] = None) -> str:
        return self._render_placeholder(placeholders)


@dc.dataclass(frozen=True)
class PlaceholderFileDeployPathPart(PlaceholderDeployPathPart, FileDeployPathPart):
    suffix: str

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.suffix:
            for c in [DEPLOY_PATH_PLACEHOLDER_PLACEHOLDER, '/']:
                check.not_in(c, self.suffix)

    def render(self, placeholders: ta.Optional[ta.Mapping[DeployPathPlaceholder, str]] = None) -> str:
        return self._render_placeholder(placeholders) + self.suffix


##


@dc.dataclass(frozen=True)
class DeployPath:
    parts: ta.Sequence[DeployPathPart]

    def __post_init__(self) -> None:
        hash(self)

        check.not_empty(self.parts)
        for p in self.parts[:-1]:
            check.equal(p.kind, 'dir')

        pd = {}
        for i, p in enumerate(self.parts):
            if isinstance(p, PlaceholderDeployPathPart):
                if p.placeholder in pd:
                    raise DeployPathError('Duplicate placeholders in path', self)
                pd[p.placeholder] = i

        if 'tag' in pd:
            if 'app' not in pd or pd['app'] >= pd['tag']:
                raise DeployPathError('Tag placeholder in path without preceding app', self)

    @property
    def kind(self) -> ta.Literal['file', 'dir']:
        return self.parts[-1].kind

    def render(self, placeholders: ta.Optional[ta.Mapping[DeployPathPlaceholder, str]] = None) -> str:
        return os.path.join(  # noqa
            *[p.render(placeholders) for p in self.parts],
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
        return cls((
            *([DirDeployPathPart.parse(p) for p in ps[:-1]] if len(ps) > 1 else []),
            tail_parse(ps[-1]),
        ))


##


class DeployPathOwner(abc.ABC):
    @abc.abstractmethod
    def get_owned_deploy_paths(self) -> ta.AbstractSet[DeployPath]:
        raise NotImplementedError


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
