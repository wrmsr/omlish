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
import typing as ta

from omlish.lite.check import check
from omlish.lite.strings import split_keep_delimiter

from ..types import DeployPathKind
from ..types import DeployPathPlaceholder


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
    placeholder: str  # DeployPathPlaceholder

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

        pd: ta.Dict[DeployPathPlaceholder, ta.List[int]] = {}
        for i, np in enumerate(self.name_parts):
            if isinstance(np, PlaceholderDeployPathNamePart):
                pd.setdefault(ta.cast(DeployPathPlaceholder, np.placeholder), []).append(i)

        # if 'tag' in pd and 'app' not in pd:
        #     raise DeployPathError('Tag placeholder in path without app', self)

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
