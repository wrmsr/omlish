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

    def __post_init__(self) -> None:
        hash(self)


##


@dc.dataclass(frozen=True)
class DeployConfSpec:
    files: ta.Optional[ta.Mapping[str, str]] = None


##


@dc.dataclass(frozen=True)
class DeploySpec:
    app: DeployApp

    git: DeployGitSpec

    venv: ta.Optional[DeployVenvSpec] = None

    conf: ta.Optional[DeployConfSpec] = None

    def __post_init__(self) -> None:
        hash(self)

    @cached_nullary
    def key(self) -> DeployKey:
        return DeployKey(hashlib.sha256(repr(self).encode('utf-8')).hexdigest()[:8])
