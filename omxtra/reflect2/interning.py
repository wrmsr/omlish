import typing as ta

from .locking import HasLock


T = ta.TypeVar('T')


##


class Interner(HasLock):
    def __init__(self, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

        self._dict: dict[object, object] = {}

    def intern(self, obj: T) -> T:
        try:
            return self._dict[obj]  # type: ignore[return-value]
        except KeyError:
            pass

        with self._lock:
            try:
                return self._dict[obj]  # type: ignore[return-value]
            except KeyError:
                pass

            self._dict[obj] = obj
            return obj


##


class HasInterner:
    def __init__(
            self,
            *,
            interner: Interner,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._interner = interner
