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
import itertools
import os.path
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.strings import split_keep_delimiter

from .types import DeployHome
from .types import DeployPathKind
from .types import DeployPathPlaceholder


##


DEPLOY_PATH_PLACEHOLDER_SIGIL = '@'
DEPLOY_PATH_PLACEHOLDER_SEPARATOR = '--'

DEPLOY_PATH_PLACEHOLDER_DELIMITERS: ta.AbstractSet[str] = frozenset([
    DEPLOY_PATH_PLACEHOLDER_SEPARATOR,
    '.',
])

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
    @classmethod
    def parse(cls, s: str) -> 'DeployPathNamePart':
        check.non_empty_str(s)
        if s.startswith(DEPLOY_PATH_PLACEHOLDER_SIGIL):
            return PlaceholderDeployPathNamePart(s[1:])
        elif s in DEPLOY_PATH_PLACEHOLDER_DELIMITERS:
            return DelimiterDeployPathNamePart(s)
        else:
            return ConstDeployPathNamePart(s)


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


@dc.dataclass(frozen=True)
class DelimiterDeployPathNamePart(DeployPathNamePart):
    delimiter: str

    def __post_init__(self) -> None:
        check.in_(self.delimiter, DEPLOY_PATH_PLACEHOLDER_DELIMITERS)

    def render(self, placeholders: ta.Optional[ta.Mapping[DeployPathPlaceholder, str]] = None) -> str:
        return self.delimiter


@dc.dataclass(frozen=True)
class ConstDeployPathNamePart(DeployPathNamePart):
    const: str

    def __post_init__(self) -> None:
        check.non_empty_str(self.const)
        for c in [*DEPLOY_PATH_PLACEHOLDER_DELIMITERS, DEPLOY_PATH_PLACEHOLDER_SIGIL, '/']:
            check.not_in(c, self.const)

    def render(self, placeholders: ta.Optional[ta.Mapping[DeployPathPlaceholder, str]] = None) -> str:
        return self.const


@dc.dataclass(frozen=True)
class DeployPathName(DeployPathRenderable):
    parts: ta.Sequence[DeployPathNamePart]

    def __post_init__(self) -> None:
        hash(self)
        check.not_empty(self.parts)
        for k, g in itertools.groupby(self.parts, type):
            if len(gl := list(g)) > 1:
                raise DeployPathError(f'May not have consecutive path name part types: {k} {gl}')

    def render(self, placeholders: ta.Optional[ta.Mapping[DeployPathPlaceholder, str]] = None) -> str:
        return ''.join(p.render(placeholders) for p in self.parts)

    @classmethod
    def parse(cls, s: str) -> 'DeployPathName':
        check.non_empty_str(s)
        check.not_in('/', s)

        i = 0
        ps = []
        while i < len(s):
            ns = [(n, d) for d in DEPLOY_PATH_PLACEHOLDER_DELIMITERS if (n := s.find(d, i)) >= 0]
            if not ns:
                ps.append(s[i:])
                break
            n, d = min(ns)
            ps.append(check.non_empty_str(s[i:n]))
            ps.append(s[n:n + len(d)])
            i = n + len(d)

        return cls(tuple(DeployPathNamePart.parse(p) for p in ps))


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
    def parse(cls, s: str) -> 'DeployPathPart':
        if (is_dir := s.endswith('/')):
            s = s[:-1]
        check.non_empty_str(s)
        check.not_in('/', s)

        n = DeployPathName.parse(s)
        if is_dir:
            return DirDeployPathPart(n)
        else:
            return FileDeployPathPart(n)


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
        return ''.join([p.render(placeholders) for p in self.parts])

    @classmethod
    def parse(cls, s: str) -> 'DeployPath':
        check.non_empty_str(s)
        ps = split_keep_delimiter(s, '/')
        return cls(tuple(DeployPathPart.parse(p) for p in ps))


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


##


class DeployPathsManager:
    def __init__(
            self,
            *,
            deploy_home: ta.Optional[DeployHome],
            deploy_path_owners: DeployPathOwners,
    ) -> None:
        super().__init__()

        self._deploy_home = deploy_home
        self._deploy_path_owners = deploy_path_owners

    @cached_nullary
    def owners_by_path(self) -> ta.Mapping[DeployPath, DeployPathOwner]:
        dct: ta.Dict[DeployPath, DeployPathOwner] = {}
        for o in self._deploy_path_owners:
            for p in o.get_owned_deploy_paths():
                if p in dct:
                    raise DeployPathError(f'Duplicate deploy path owner: {p}')
                dct[p] = o
        return dct

    def validate_deploy_paths(self) -> None:
        self.owners_by_path()
