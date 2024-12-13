# ruff: noqa: UP006 UP007
import abc
import typing as ta


DeployAtomicPathSwapState = ta.Literal['new', 'open', 'committed', 'aborted']  # ta.TypeAlias


class DeployAtomicPathSwap(abc.ABC):
    def __init__(
            self,
            *,
            auto_commit: bool = False,
    ) -> None:
        super().__init__()

        self._auto_commit = auto_commit

        self._state: DeployAtomicPathSwapState = 'new'

    #

    @property
    def state(self) -> DeployAtomicPathSwapState:
        return self._state

    def _check_state(self, *states: DeployAtomicPathSwapState) -> None:
        if self._state not in states:
            raise RuntimeError('Atomic path swap not in correct state: %r, %r', self._state, states)

    #

    @abc.abstractmethod
    def _open(self) -> None:
        raise NotImplementedError

    def open(self) -> None:
        if self._state == 'open':
            return
        self._check_state('new')
        self._commit()

    #

    @abc.abstractmethod
    def _commit(self) -> None:
        raise NotImplementedError

    def commit(self) -> None:
        if self._state == 'committed':
            return
        self._check_state('open')
        self._commit()

    #

    @abc.abstractmethod
    def _abort(self) -> None:
        raise NotImplementedError

    def abort(self) -> None:
        if self._state == 'aborted':
            return
        self._check_state('open')
        self._abort()

    #

    def __enter__(self) -> 'DeployAtomicPathSwap':
        self.open()
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
