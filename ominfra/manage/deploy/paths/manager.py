# ruff: noqa: UP006 UP007 UP045
import typing as ta

from omlish.lite.cached import cached_nullary

from .owners import DeployPathOwner
from .owners import DeployPathOwners
from .paths import DeployPath
from .paths import DeployPathError


##


class DeployPathsManager:
    def __init__(
            self,
            *,
            deploy_path_owners: DeployPathOwners,
    ) -> None:
        super().__init__()

        self._deploy_path_owners = deploy_path_owners

    @cached_nullary
    def owners_by_path(self) -> ta.Mapping[DeployPath, DeployPathOwner]:
        dct: ta.Dict[DeployPath, DeployPathOwner] = {}
        for o in self._deploy_path_owners:
            for p in o.get_owned_deploy_paths():
                if p in dct:
                    raise DeployPathError(f'Duplicate deploy path owner: {p}')
                dct[p] = o
        return dct

    def validate_deploy_paths(self) -> None:
        self.owners_by_path()
