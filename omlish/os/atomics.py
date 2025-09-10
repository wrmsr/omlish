# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import os
import shutil
import tempfile
import typing as ta

from ..lite.abstract import Abstract
from ..lite.attrops import attr_repr
from ..lite.check import check


AtomicPathSwapKind = ta.Literal['dir', 'file']  # ta.TypeAlias
AtomicPathSwapState = ta.Literal['open', 'committed', 'aborted']  # ta.TypeAlias


##


class AtomicPathSwap(Abstract):
    def __init__(
            self,
            kind: AtomicPathSwapKind,
            dst_path: str,
            *,
            auto_commit: bool = False,
    ) -> None:
        super().__init__()

        self._kind = kind
        self._dst_path = dst_path
        self._auto_commit = auto_commit

        self._state: AtomicPathSwapState = 'open'

    def __repr__(self) -> str:
        return attr_repr(self, 'kind', 'dst_path', 'tmp_path')

    @property
    def kind(self) -> AtomicPathSwapKind:
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
    def state(self) -> AtomicPathSwapState:
        return self._state

    def _check_state(self, *states: AtomicPathSwapState) -> None:
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

    def __enter__(self) -> 'AtomicPathSwap':
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


class AtomicPathSwapping(Abstract):
    @abc.abstractmethod
    def begin_atomic_path_swap(
            self,
            kind: AtomicPathSwapKind,
            dst_path: str,
            *,
            name_hint: ta.Optional[str] = None,
            make_dirs: bool = False,
            skip_root_dir_check: bool = False,
            **kwargs: ta.Any,
    ) -> AtomicPathSwap:
        raise NotImplementedError


##


class OsReplaceAtomicPathSwap(AtomicPathSwap):
    def __init__(
            self,
            kind: AtomicPathSwapKind,
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
        os.replace(self._tmp_path, self._dst_path)

    def _abort(self) -> None:
        shutil.rmtree(self._tmp_path, ignore_errors=True)


class TempDirAtomicPathSwapping(AtomicPathSwapping):
    def __init__(
            self,
            *,
            temp_dir: ta.Optional[str] = None,
            root_dir: ta.Optional[str] = None,
    ) -> None:
        super().__init__()

        if root_dir is not None:
            root_dir = os.path.abspath(root_dir)
        self._root_dir = root_dir
        self._temp_dir = temp_dir

    def begin_atomic_path_swap(
            self,
            kind: AtomicPathSwapKind,
            dst_path: str,
            *,
            name_hint: ta.Optional[str] = None,
            make_dirs: bool = False,
            skip_root_dir_check: bool = False,
            **kwargs: ta.Any,
    ) -> AtomicPathSwap:
        dst_path = os.path.abspath(dst_path)
        if (
                not skip_root_dir_check and
                self._root_dir is not None and
                not dst_path.startswith(check.non_empty_str(self._root_dir))
        ):
            raise RuntimeError(f'Atomic path swap dst must be in root dir: {dst_path}, {self._root_dir}')

        dst_dir = os.path.dirname(dst_path)
        if make_dirs:
            os.makedirs(dst_dir, exist_ok=True)
        if not os.path.isdir(dst_dir):
            raise RuntimeError(f'Atomic path swap dst dir does not exist: {dst_dir}')

        if kind == 'dir':
            tmp_path = tempfile.mkdtemp(prefix=name_hint, dir=self._temp_dir)
        elif kind == 'file':
            fd, tmp_path = tempfile.mkstemp(prefix=name_hint, dir=self._temp_dir)
            os.close(fd)
        else:
            raise TypeError(kind)

        return OsReplaceAtomicPathSwap(
            kind,
            dst_path,
            tmp_path,
            **kwargs,
        )
