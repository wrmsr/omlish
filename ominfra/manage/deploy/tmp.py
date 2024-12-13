# ruff: noqa: UP006 UP007
import os.path
import tempfile
import typing as ta

from omlish.lite.check import check

from .atomic import DeployAtomicPathSwap
from .atomic import DeployAtomicPathSwapKind
from .atomic import DeployAtomicPathSwapping
from .atomic import OsRenameDeployAtomicPathSwap
from .paths import SingleDirDeployPathOwner
from .types import DeployHome


class DeployTmpManager(
    SingleDirDeployPathOwner,
    DeployAtomicPathSwapping,
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

    def begin_atomic_path_swap(
            self,
            kind: DeployAtomicPathSwapKind,
            dst_path: str,
            *,
            name_hint: ta.Optional[str] = None,
    ) -> DeployAtomicPathSwap:
        dst_path = os.path.abspath(dst_path)
        if not dst_path.startswith(check.non_empty_str(self._deploy_home)):
            raise RuntimeError(f'Atomic path swap dst must be in deploy home: {dst_path}, {self._deploy_home}')

        if kind == 'dir':
            tmp_path = tempfile.mkdtemp(prefix=name_hint, dir=self._dir())
        elif kind == 'file':
            fd, tmp_path = tempfile.mkstemp(prefix=name_hint, dir=self._dir())
            os.close(fd)
        else:
            raise TypeError(kind)

        return OsRenameDeployAtomicPathSwap(
            kind,
            dst_path,
            tmp_path,
        )
