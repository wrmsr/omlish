# ruff: noqa: UP006 UP007 UP045
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

from omlish.lite.abstract import Abstract
from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.strings import split_keep_delimiter

from ..tags import DEPLOY_TAG_DELIMITERS
from ..tags import DEPLOY_TAG_SIGIL
from ..tags import DEPLOY_TAGS_BY_NAME
from ..tags import DeployTag
from ..tags import DeployTagMap
from .types import DeployPathKind


##


class DeployPathError(Exception):
    pass


class DeployPathRenderable(Abstract):
    @cached_nullary
    def __str__(self) -> str:
        return self.render(None)

    @abc.abstractmethod
    def render(self, tags: ta.Optional[DeployTagMap] = None) -> str:
        raise NotImplementedError


##


class DeployPathNamePart(DeployPathRenderable, Abstract):
    @classmethod
    def parse(cls, s: str) -> 'DeployPathNamePart':
        check.non_empty_str(s)
        if s.startswith(DEPLOY_TAG_SIGIL):
            return TagDeployPathNamePart(s[1:])
        elif s in DEPLOY_TAG_DELIMITERS:
            return DelimiterDeployPathNamePart(s)
        else:
            return ConstDeployPathNamePart(s)


@dc.dataclass(frozen=True)
class TagDeployPathNamePart(DeployPathNamePart):
    name: str

    def __post_init__(self) -> None:
        check.in_(self.name, DEPLOY_TAGS_BY_NAME)

    @property
    def tag(self) -> ta.Type[DeployTag]:
        return DEPLOY_TAGS_BY_NAME[self.name]

    def render(self, tags: ta.Optional[DeployTagMap] = None) -> str:
        if tags is not None:
            return tags[self.tag].s
        else:
            return DEPLOY_TAG_SIGIL + self.name


@dc.dataclass(frozen=True)
class DelimiterDeployPathNamePart(DeployPathNamePart):
    delimiter: str

    def __post_init__(self) -> None:
        check.in_(self.delimiter, DEPLOY_TAG_DELIMITERS)

    def render(self, tags: ta.Optional[DeployTagMap] = None) -> str:
        return self.delimiter


@dc.dataclass(frozen=True)
class ConstDeployPathNamePart(DeployPathNamePart):
    const: str

    def __post_init__(self) -> None:
        check.non_empty_str(self.const)
        for c in [*DEPLOY_TAG_DELIMITERS, DEPLOY_TAG_SIGIL, '/']:
            check.not_in(c, self.const)

    def render(self, tags: ta.Optional[DeployTagMap] = None) -> str:
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

    def render(self, tags: ta.Optional[DeployTagMap] = None) -> str:
        return ''.join(p.render(tags) for p in self.parts)

    @classmethod
    def parse(cls, s: str) -> 'DeployPathName':
        check.non_empty_str(s)
        check.not_in('/', s)

        i = 0
        ps = []
        while i < len(s):
            ns = [(n, d) for d in DEPLOY_TAG_DELIMITERS if (n := s.find(d, i)) >= 0]
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
class DeployPathPart(DeployPathRenderable, Abstract):
    name: DeployPathName

    @property
    @abc.abstractmethod
    def kind(self) -> DeployPathKind:
        raise NotImplementedError

    def render(self, tags: ta.Optional[DeployTagMap] = None) -> str:
        return self.name.render(tags) + ('/' if self.kind == 'dir' else '')

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


##


@dc.dataclass(frozen=True)
class DeployPath(DeployPathRenderable):
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

    @cached_nullary
    def tag_indices(self) -> ta.Mapping[ta.Type[DeployTag], ta.Sequence[int]]:
        pd: ta.Dict[ta.Type[DeployTag], ta.List[int]] = {}
        for i, np in enumerate(self.name_parts):
            if isinstance(np, TagDeployPathNamePart):
                pd.setdefault(np.tag, []).append(i)
        return pd

    @property
    def kind(self) -> DeployPathKind:
        return self.parts[-1].kind

    def render(self, tags: ta.Optional[DeployTagMap] = None) -> str:
        return ''.join([p.render(tags) for p in self.parts])

    @classmethod
    def parse(cls, s: str) -> 'DeployPath':
        check.non_empty_str(s)
        ps = split_keep_delimiter(s, '/')
        return cls(tuple(DeployPathPart.parse(p) for p in ps))
