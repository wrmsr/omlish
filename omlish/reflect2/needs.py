import threading
import typing as ta


if ta.TYPE_CHECKING:
    from .interning import Interner
    from .reflector import TypeReflector
    from .universe import TypeUniverse


##


class NeedsLock:
    def __init__(self, *, lock: threading.RLock, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

        self._lock = lock


##


class NeedsInterner:
    def __init__(self, *, interner: Interner, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

        self._interner = interner


##


class NeedsUniverse:
    def __init__(self, *, universe: TypeUniverse, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

        self._universe = universe


##


class NeedsReflector:
    def __init__(self, *, reflector: TypeReflector, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

        self._reflector = reflector
