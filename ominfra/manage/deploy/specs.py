# ruff: noqa: UP006 UP007
import dataclasses as dc
import hashlib
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check

from .types import DeployApp
from .types import DeployKey
from .types import DeployRev


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
        check.non_empty_str(self.path)
        check.not_in('..', self.path)
        check.arg(not self.path.startswith('/'))


@dc.dataclass(frozen=True)
class DeployConfSpec:
    files: ta.Optional[ta.Sequence[DeployConfFile]] = None

    dir_links: ta.Sequence[str] = ()

    def __post_init__(self) -> None:
        if self.files:
            seen: ta.Set[str] = set()
            for f in self.files:
                check.not_in(f.path, seen)
                seen.add(f.path)

        for dl in self.dir_links:
            check.non_empty_str(dl)
            check.arg(not any(c in dl for c in ('.', '/')))


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
