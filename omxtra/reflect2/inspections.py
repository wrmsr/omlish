import typing as ta

from .locking import HasLock


##


class InspectionCache(HasLock):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self._inspection_cache: dict[tuple[str, object], object] = {}

    #

    def _cached_inspection(
            self,
            kind: str,
            obj: object,
            factory: ta.Callable[[], object],
    ) -> object:
        key = (kind, obj)
        try:
            return self._inspection_cache[key]
        except KeyError:
            pass
        except TypeError:
            return factory()

        ret = factory()
        try:
            self._inspection_cache[key] = ret
        except TypeError:
            pass
        return ret

    def cached_inspection(
            self,
            kind: str,
            obj: object,
            factory: ta.Callable[[], object],
    ) -> object:
        key = (kind, obj)
        try:
            return self._inspection_cache[key]
        except KeyError:
            pass
        except TypeError:
            return factory()

        with self._lock:
            return self._cached_inspection(kind, obj, factory)
