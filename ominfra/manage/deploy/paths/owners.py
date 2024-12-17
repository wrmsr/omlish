# ruff: noqa: UP006 UP007
import abc
import os.path
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check

from ..types import DeployHome
from .paths import DeployPath



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
