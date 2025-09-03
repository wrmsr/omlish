# ruff: noqa: UP006 UP007 UP045
import abc
import os.path
import typing as ta

from omlish.lite.abstract import Abstract
from omlish.lite.check import check

from ..types import DeployHome
from .paths import DeployPath


##


class DeployPathOwner(Abstract):
    @abc.abstractmethod
    def get_owned_deploy_paths(self) -> ta.AbstractSet[DeployPath]:
        raise NotImplementedError


DeployPathOwners = ta.NewType('DeployPathOwners', ta.Sequence[DeployPathOwner])


class SingleDirDeployPathOwner(DeployPathOwner, Abstract):
    def __init__(
            self,
            *args: ta.Any,
            owned_dir: str,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        check.not_in('/', owned_dir)
        self._owned_dir: str = check.non_empty_str(owned_dir)

        self._owned_deploy_paths = frozenset([DeployPath.parse(self._owned_dir + '/')])

    def _dir(self, home: DeployHome) -> str:
        return os.path.join(check.non_empty_str(home), self._owned_dir)

    def _make_dir(self, home: DeployHome) -> str:
        if not os.path.isdir(d := self._dir(home)):
            os.makedirs(d, exist_ok=True)
        return d

    def get_owned_deploy_paths(self) -> ta.AbstractSet[DeployPath]:
        return self._owned_deploy_paths
