# ruff: noqa: UP006 UP007
from omlish.lite.check import check
from omlish.os.atomics import AtomicPathSwapping
from omlish.os.atomics import TempDirAtomicPathSwapping

from .paths.owners import SingleDirDeployPathOwner
from .types import DeployHome


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
