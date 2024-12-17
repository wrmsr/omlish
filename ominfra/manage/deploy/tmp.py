# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.os.atomics import AtomicPathSwap
from omlish.os.atomics import AtomicPathSwapKind
from omlish.os.atomics import AtomicPathSwapping
from omlish.os.atomics import TempDirAtomicPathSwapping

from .paths.owners import SingleDirDeployPathOwner
from .types import DeployHome


class DeployTmpManager(
    SingleDirDeployPathOwner,
    AtomicPathSwapping,
):
    def __init__(
            self,
            *,
            deploy_home: ta.Optional[DeployHome] = None,
    ) -> None:
        super().__init__(
            owned_dir='tmp',
            deploy_home=deploy_home,
        )

    @cached_nullary
    def _swapping(self) -> AtomicPathSwapping:
        return TempDirAtomicPathSwapping(
            temp_dir=self._make_dir(),
            root_dir=check.non_empty_str(self._deploy_home),
        )

    def begin_atomic_path_swap(
            self,
            kind: AtomicPathSwapKind,
            dst_path: str,
            **kwargs: ta.Any,
    ) -> AtomicPathSwap:
        return self._swapping().begin_atomic_path_swap(
            kind,
            dst_path,
            **kwargs,
        )
