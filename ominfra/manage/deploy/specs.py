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
        hash(self)
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
class DeployConfFile:
    path: str
    body: str

    def __post_init__(self) -> None:
        check_valid_deploy_spec_path(self.path)


#


@dc.dataclass(frozen=True)
class DeployConfLink(abc.ABC):  # noqa
    """
    May be either:
     - @conf(.ext)* - links a single file in root of app conf dir to conf/@conf/@dst(.ext)*
     - @conf/ - links a directory in root of app conf dir to conf/@conf/@dst/
    """

    src: str

    def __post_init__(self) -> None:
        check_valid_deploy_spec_path(self.src)
        if '/' in self.src:
            check.equal(self.src.count('/'), 1)
            check.arg(self.src.endswith('/'))


class AppDeployConfLink(DeployConfLink):
    pass


class TagDeployConfLink(DeployConfLink):
    pass


#


@dc.dataclass(frozen=True)
class DeployConfSpec:
    files: ta.Optional[ta.Sequence[DeployConfFile]] = None

    links: ta.Optional[ta.Sequence[DeployConfLink]] = None

    def __post_init__(self) -> None:
        if self.files:
            seen: ta.Set[str] = set()
            for f in self.files:
                check.not_in(f.path, seen)
                seen.add(f.path)


##


@dc.dataclass(frozen=True)
class DeploySpec:
    app: DeployApp

    git: DeployGitSpec

    venv: ta.Optional[DeployVenvSpec] = None

    conf: ta.Optional[DeployConfSpec] = None

    @cached_nullary
    def key(self) -> DeployKey:
        return DeployKey(hashlib.sha256(repr(self).encode('utf-8')).hexdigest()[:8])
