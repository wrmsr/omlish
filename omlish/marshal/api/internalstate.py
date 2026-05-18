# ruff: noqa: SLF001
"""
Keying axes:
 - None - polymorphism.metadata
 - (weak) config - lazyinit
   - (also, like, identity-keyed to the tv collection provided tuple of configs.get().get(LazyInit))
 - (weak) config + (weak) factory - typecache
"""
import threading
import typing as ta
import weakref

from ... import lang
from .configs import ConfigRegistry


if ta.TYPE_CHECKING:
    from .types import Handler


InternalStateEntryT = ta.TypeVar('InternalStateEntryT', bound='InternalState.Entry')
InternalStateByConfigEntryT = ta.TypeVar('InternalStateByConfigEntryT', bound='InternalState.ByConfig.Entry')
InternalStateByConfigByHandlerEntryT = ta.TypeVar('InternalStateByConfigByHandlerEntryT', bound='InternalState.ByConfig.ByHandler.Entry')  # noqa


##


class _AnyInternalStateEntry(lang.Abstract):
    pass


@ta.final
class InternalState:
    def __init__(self) -> None:
        super().__init__()

        self._lock = threading.RLock()

        self._entries: dict[
            type[InternalState.Entry],
            InternalState.Entry,
        ] = {}

        self._by_config: ta.MutableMapping[
            ConfigRegistry,
            InternalState.ByConfig,
        ] = weakref.WeakKeyDictionary()

    #

    class Entry(_AnyInternalStateEntry, lang.Abstract):
        pass

    def get(
            self,
            ty: type[InternalStateEntryT],
            new: ta.Callable[[], InternalStateEntryT] | None = None,
            /,
    ) -> InternalStateEntryT:
        try:
            return self._entries[ty]  # type: ignore[return-value]
        except KeyError:
            with self._lock:
                try:
                    return self._entries[ty]  # type: ignore[return-value]
                except KeyError:
                    entry = self._entries[ty] = (new if new is not None else ty)()
                    return entry

    #

    def by_config(self, cfg: ConfigRegistry, /) -> ByConfig:
        try:
            return self._by_config[cfg]
        except KeyError:
            with self._lock:
                try:
                    return self._by_config[cfg]
                except KeyError:
                    by_config = self._by_config[cfg] = InternalState.ByConfig(_o=self)
                    return by_config

    @ta.final
    class ByConfig:
        def __init__(self, *, _o: InternalState) -> None:
            self._o = _o

            self._entries: dict[
                type[InternalState.ByConfig.Entry],
                InternalState.ByConfig.Entry,
            ] = {}

            self._by_handler: ta.MutableMapping[
                Handler,
                InternalState.ByConfig.ByHandler,
            ] = weakref.WeakKeyDictionary()

        #

        class Entry(_AnyInternalStateEntry, lang.Abstract):
            pass

        def get(
                self,
                ty: type[InternalStateByConfigEntryT],
                new: ta.Callable[[], InternalStateByConfigEntryT] | None = None,
                /,
        ) -> InternalStateByConfigEntryT:
            try:
                return self._entries[ty]  # type: ignore[return-value]
            except KeyError:
                with self._o._lock:
                    try:
                        return self._entries[ty]  # type: ignore[return-value]
                    except KeyError:
                        entry = self._entries[ty] = (new if new is not None else ty)()
                        return entry

        #

        def by_handler(self, fac: Handler, /) -> ByHandler:
            try:
                return self._by_handler[fac]
            except KeyError:
                with self._o._lock:
                    try:
                        return self._by_handler[fac]
                    except KeyError:
                        by_handler = self._by_handler[fac] = InternalState.ByConfig.ByHandler(_o=self)
                        return by_handler

        @ta.final
        class ByHandler:
            def __init__(self, *, _o: InternalState.ByConfig) -> None:
                self._o = _o

                self._entries: dict[
                    type[InternalState.ByConfig.ByHandler.Entry],
                    InternalState.ByConfig.ByHandler.Entry,
                ] = {}

            #

            class Entry(_AnyInternalStateEntry, lang.Abstract):
                pass

            def get(
                    self,
                    ty: type[InternalStateByConfigByHandlerEntryT],
                    new: ta.Callable[[], InternalStateByConfigByHandlerEntryT] | None = None,
                    /,
            ) -> InternalStateByConfigByHandlerEntryT:
                try:
                    return self._entries[ty]  # type: ignore[return-value]
                except KeyError:
                    with self._o._o._lock:
                        try:
                            return self._entries[ty]  # type: ignore[return-value]
                        except KeyError:
                            entry = self._entries[ty] = (new if new is not None else ty)()
                            return entry
