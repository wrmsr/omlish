# ruff: noqa: UP006 UP007
import abc
import typing as ta


class DeployAtomicPathSwap(abc.ABC):
    def __init__(
            self,
            *,
            auto_commit: bool = False,
    ) -> None:
        super().__init__()

        self._auto_commit = auto_commit

        self._state: ta.Literal['new', 'open', 'committed', 'aborted'] = 'new'

    @property
    def state(self) -> ta.Literal['new', 'open', 'committed', 'aborted']:
        return self._state

    def _check_open(self) -> None:
        if self._state != 'open':
            raise RuntimeError('Atomic path swap not open')

    @abc.abstractmethod
    def _commit(self) -> None:
        raise NotImplementedError

    def commit(self) -> None:
        if self._state == 'committed':
            return
        self._check_open()
        self._commit()

    @abc.abstractmethod
    def _abort(self) -> None:
        raise NotImplementedError

    def abort(self) -> None:
        if self._state == 'aborted':
            return
        self._check_open()
        self._abort()

    def __enter__(self) -> 'DeployAtomicPathSwap':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._state == 'new':
            pass
        elif (
                exc_type is None and
                self._auto_commit and
                self._state == 'open'
        ):
            self.commit()
        else:
            self.abort()


class DeployAtomicPathSwapping(abc.ABC):
    @abc.abstractmethod
    def begin_atomic_path_swap(self) -> DeployAtomicPathSwap:
        raise NotImplementedError
