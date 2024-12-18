# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import hashlib
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check

from .types import DeployApp
from .types import DeployKey
from .types import DeployRev


##


def check_valid_deploy_spec_path(s: str) -> str:
    check.non_empty_str(s)
    for c in ['..', '//']:
        check.not_in(c, s)
    check.arg(not s.startswith('/'))
    return s


class _DeploySpecKeyed:
    @cached_nullary
    def key(self) -> DeployKey:
        return DeployKey(hashlib.sha256(repr(self).encode('utf-8')).hexdigest()[:8])


##


@dc.dataclass(frozen=True)
class DeployGitRepo:
    host: ta.Optional[str] = None
    username: ta.Optional[str] = None
    path: ta.Optional[str] = None

    def __post_init__(self) -> None:
        check.not_in('..', check.non_empty_str(self.host))
        check.not_in('.', check.non_empty_str(self.path))


@dc.dataclass(frozen=True)
class DeployGitSpec:
    repo: DeployGitRepo
    rev: DeployRev

    subtrees: ta.Optional[ta.Sequence[str]] = None

    def __post_init__(self) -> None:
        check.non_empty_str(self.rev)
        if self.subtrees is not None:
            for st in self.subtrees:
                check.non_empty_str(st)


##


@dc.dataclass(frozen=True)
class DeployVenvSpec:
    interp: ta.Optional[str] = None

    requirements_files: ta.Optional[ta.Sequence[str]] = None
    extra_dependencies: ta.Optional[ta.Sequence[str]] = None

    use_uv: bool = False


##


@dc.dataclass(frozen=True)
class DeployAppConfFile:
    path: str
    body: str

    def __post_init__(self) -> None:
        check_valid_deploy_spec_path(self.path)


#


@dc.dataclass(frozen=True)
class DeployAppConfLink(abc.ABC):  # noqa
    """
    May be either:
     - @conf(.ext)* - links a single file in root of app conf dir to conf/@conf/@dst(.ext)*
     - @conf/file - links a single file in a single subdir to conf/@conf/@dst--file
     - @conf/ - links a directory in root of app conf dir to conf/@conf/@dst/
    """

    src: str

    def __post_init__(self) -> None:
        check_valid_deploy_spec_path(self.src)
        if '/' in self.src:
            check.equal(self.src.count('/'), 1)


class AppDeployAppConfLink(DeployAppConfLink):
    pass


class TagDeployAppConfLink(DeployAppConfLink):
    pass


#


@dc.dataclass(frozen=True)
class DeployAppConfSpec:
    files: ta.Optional[ta.Sequence[DeployAppConfFile]] = None

    links: ta.Optional[ta.Sequence[DeployAppConfLink]] = None

    def __post_init__(self) -> None:
        if self.files:
            seen: ta.Set[str] = set()
            for f in self.files:
                check.not_in(f.path, seen)
                seen.add(f.path)


##


@dc.dataclass(frozen=True)
class DeployAppSpec(_DeploySpecKeyed):
    app: DeployApp

    git: DeployGitSpec

    venv: ta.Optional[DeployVenvSpec] = None

    conf: ta.Optional[DeployAppConfSpec] = None

    def __post_init__(self) -> None:
        check.non_empty_str(self.app)

##


@dc.dataclass(frozen=True)
class DeploySpec(_DeploySpecKeyed):
    apps: ta.Sequence[DeployAppSpec]

    def __post_init__(self) -> None:
        seen: ta.Set[DeployApp] = set()
        for a in self.apps:
            if a.app in seen:
                raise KeyError(a.app)
            seen.add(a.app)
