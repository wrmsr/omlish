# ruff: noqa: UP006 UP007
import abc
import os
import shutil
import typing as ta

from omlish.lite.check import check
from omlish.lite.strings import attr_repr


DeployAtomicPathSwapKind = ta.Literal['dir', 'file']
DeployAtomicPathSwapState = ta.Literal['open', 'committed', 'aborted']  # ta.TypeAlias


##


class DeployAtomicPathSwap(abc.ABC):
    def __init__(
            self,
            kind: DeployAtomicPathSwapKind,
            dst_path: str,
            *,
            auto_commit: bool = False,
    ) -> None:
        super().__init__()

        self._kind = kind
        self._dst_path = dst_path
        self._auto_commit = auto_commit

        self._state: DeployAtomicPathSwapState = 'open'

    def __repr__(self) -> str:
        return attr_repr(self, 'kind', 'dst_path', 'tmp_path')

    @property
    def kind(self) -> DeployAtomicPathSwapKind:
        return self._kind

    @property
    def dst_path(self) -> str:
        return self._dst_path

    @property
    @abc.abstractmethod
    def tmp_path(self) -> str:
        raise NotImplementedError

    #

    @property
    def state(self) -> DeployAtomicPathSwapState:
        return self._state

    def _check_state(self, *states: DeployAtomicPathSwapState) -> None:
        if self._state not in states:
            raise RuntimeError(f'Atomic path swap not in correct state: {self._state}, {states}')

    #

    @abc.abstractmethod
    def _commit(self) -> None:
        raise NotImplementedError

    def commit(self) -> None:
        if self._state == 'committed':
            return
        self._check_state('open')
        try:
            self._commit()
        except Exception:  # noqa
            self._abort()
            raise
        else:
            self._state = 'committed'

    #

    @abc.abstractmethod
    def _abort(self) -> None:
        raise NotImplementedError

    def abort(self) -> None:
        if self._state == 'aborted':
            return
        self._abort()
        self._state = 'aborted'

    #

    def __enter__(self) -> 'DeployAtomicPathSwap':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if (
                exc_type is None and
                self._auto_commit and
                self._state == 'open'
        ):
            self.commit()
        else:
            self.abort()


#


class DeployAtomicPathSwapping(abc.ABC):
    @abc.abstractmethod
    def begin_atomic_path_swap(
            self,
            kind: DeployAtomicPathSwapKind,
            dst_path: str,
            *,
            name_hint: ta.Optional[str] = None,
    ) -> DeployAtomicPathSwap:
        raise NotImplementedError


##


class OsRenameDeployAtomicPathSwap(DeployAtomicPathSwap):
    def __init__(
            self,
            kind: DeployAtomicPathSwapKind,
            dst_path: str,
            tmp_path: str,
            **kwargs: ta.Any,
    ) -> None:
        if kind == 'dir':
            check.state(os.path.isdir(tmp_path))
        elif kind == 'file':
            check.state(os.path.isfile(tmp_path))
        else:
            raise TypeError(kind)

        super().__init__(
            kind,
            dst_path,
            **kwargs,
        )

        self._tmp_path = tmp_path

    @property
    def tmp_path(self) -> str:
        return self._tmp_path

    def _commit(self) -> None:
        os.rename(self._tmp_path, self._dst_path)

    def _abort(self) -> None:
        shutil.rmtree(self._tmp_path, ignore_errors=True)
