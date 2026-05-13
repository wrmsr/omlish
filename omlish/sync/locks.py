import threading
import typing as ta


##


class AttemptedReentrantAcquireLockError(RuntimeError):
    pass


class AttemptedUnownedReleaseLockError(RuntimeError):
    pass


class StrictLock:
    """
    A non-reentrant mutex that raises on attempted same-thread reentry.

    Unlike threading.Lock, this detects self-deadlock attempts and raises RuntimeError instead of blocking forever.

    Semantics:
      - Only the owning thread may release.
      - Reentrant acquire by owner raises.
      - Otherwise behaves like a normal Lock.
      - Supports `with` statements.
    """

    def __init__(self) -> None:
        super().__init__()

        self._lock = threading.Lock()
        self._owner: int | None = None

    #

    @property
    def owner(self) -> int | None:
        return self._owner

    def locked(self) -> bool:
        return self._lock.locked()

    def __repr__(self) -> str:
        state = 'locked' if self.locked() else 'unlocked'
        return (
            f'{self.__class__.__name__}'
            f'({state}, owner={self._owner!r})'
        )

    #

    def acquire(
            self,
            blocking: bool = True,
            timeout: float = -1,
    ) -> bool:
        ident = threading.get_ident()

        if self._owner == ident:
            raise AttemptedReentrantAcquireLockError

        acquired = self._lock.acquire(blocking, timeout)

        if acquired:
            # Ownership must be recorded only after successful acquire.
            self._owner = ident

        return acquired

    def release(self) -> None:
        ident = threading.get_ident()

        if self._owner != ident:
            raise AttemptedUnownedReleaseLockError

        # Clear owner before unlock so state remains consistent even if another thread immediately acquires after
        # release().
        self._owner = None
        self._lock.release()

    def __enter__(self) -> ta.Self:
        self.acquire()
        return self

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: ta.Any,
    ) -> None:
        self.release()
