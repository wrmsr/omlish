"""
Keying axes:
 - None - polymorphism.metadata
 - (weak) config - lazyinit
   - (also, like, identity-keyed to the tv collection provided tuple of configs.get().get(LazyInit))
 - (weak) config + (weak) factory - typecache
"""
from ... import lang


##


class InternalStateEntry(lang.Abstract):
    pass


class InternalState:
    def __init__(self) -> None:
        super().__init__()

        self._entries: dict[type[InternalStateEntry], InternalStateEntry] = {}
