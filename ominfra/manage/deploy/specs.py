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


##


@dc.dataclass(frozen=True)
class DeploySpec:
    app: DeployApp
    repo: DeployGitRepo
    rev: DeployRev

    def __post_init__(self) -> None:
        hash(self)

    @cached_nullary
    def key(self) -> DeployKey:
        return DeployKey(hashlib.sha256(repr(self).encode('utf-8')).hexdigest()[:8])
