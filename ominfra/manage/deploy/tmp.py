# ruff: noqa: UP006 UP007
import typing as ta

from .paths import SingleDirDeployPathOwner
from .types import DeployHome


class DeployTmpManager(SingleDirDeployPathOwner):
    def __init__(
            self,
            *,
            deploy_home: ta.Optional[DeployHome] = None,
    ) -> None:
        super().__init__(
            owned_dir='tmp',
            deploy_home=deploy_home,
        )
