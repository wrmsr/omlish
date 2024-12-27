# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import hashlib
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check

from .conf.specs import DeployAppConfSpec
from .tags import DeployApp
from .tags import DeployAppKey
from .tags import DeployKey
from .tags import KeyDeployTag  # noqa
from .types import DeployHome
from .types import DeployRev


KeyDeployTagT = ta.TypeVar('KeyDeployTagT', bound='KeyDeployTag')


##


class DeploySpecKeyed(ta.Generic[KeyDeployTagT]):
    @cached_nullary
    def _key_str(self) -> str:
        return hashlib.sha256(repr(self).encode('utf-8')).hexdigest()[:8]

    @abc.abstractmethod
    def key(self) -> KeyDeployTagT:
        raise NotImplementedError


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

    shallow: bool = False

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
class DeployAppSpec(DeploySpecKeyed[DeployAppKey]):
    app: DeployApp

    git: DeployGitSpec

    venv: ta.Optional[DeployVenvSpec] = None

    conf: ta.Optional[DeployAppConfSpec] = None

    # @ta.override
    def key(self) -> DeployAppKey:
        return DeployAppKey(self._key_str())


@dc.dataclass(frozen=True)
class DeployAppLinksSpec:
    apps: ta.Sequence[DeployApp] = ()

    removed_apps: ta.Sequence[DeployApp] = ()

    exclude_unspecified: bool = False


##


@dc.dataclass(frozen=True)
class DeploySystemdSpec:
    # ~/.config/systemd/user/
    unit_dir: ta.Optional[str] = None


##


@dc.dataclass(frozen=True)
class DeploySpec(DeploySpecKeyed[DeployKey]):
    home: DeployHome

    apps: ta.Sequence[DeployAppSpec] = ()

    app_links: DeployAppLinksSpec = DeployAppLinksSpec()

    systemd: ta.Optional[DeploySystemdSpec] = None

    def __post_init__(self) -> None:
        check.non_empty_str(self.home)

        seen: ta.Set[DeployApp] = set()
        for a in self.apps:
            if a.app in seen:
                raise KeyError(a.app)
            seen.add(a.app)

    # @ta.override
    def key(self) -> DeployKey:
        return DeployKey(self._key_str())
