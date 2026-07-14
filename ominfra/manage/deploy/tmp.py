# ruff: noqa: UP006 UP007 UP045
from omcore.lite.check import check
from omcore.lite.typing import Func1
from omcore.os.atomics import AtomicPathSwapping
from omcore.os.atomics import TempDirAtomicPathSwapping

from .paths.owners import SingleDirDeployPathOwner
from .types import DeployHome


##


class DeployHomeAtomics(Func1[DeployHome, AtomicPathSwapping]):
    pass


class DeployTmpManager(
    SingleDirDeployPathOwner,
):
    def __init__(self) -> None:
        super().__init__(
            owned_dir='tmp',
        )

    def get_swapping(self, home: DeployHome) -> AtomicPathSwapping:
        return TempDirAtomicPathSwapping(
            temp_dir=self._make_dir(home),
            root_dir=check.non_empty_str(home),
        )
