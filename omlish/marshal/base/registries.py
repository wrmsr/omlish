"""
TODO:
 - col.TypeMap?
  - at least get_any
 - sheesh threadsafe this junk
"""
import dataclasses as dc
import threading
import typing as ta

from ... import collections as col
from ... import lang


##


class RegistryItem(lang.Abstract):
    pass


RegistryItemT = ta.TypeVar('RegistryItemT', bound=RegistryItem)
RegistryItemU = ta.TypeVar('RegistryItemU', bound=RegistryItem)


@dc.dataclass(frozen=True)
class _KeyRegistryItems(ta.Generic[RegistryItemT]):
    key: ta.Any
    items: ta.Sequence[RegistryItemT] = ()
    item_lists_by_ty: ta.Mapping[type[RegistryItemT], ta.Sequence[RegistryItemT]] = dc.field(default_factory=dict)

    def add(self, *items: RegistryItemT) -> '_KeyRegistryItems':
        item_lists_by_ty: dict[type[RegistryItemT], list[RegistryItemT]] = {}
        for i in items:
            try:
                l = item_lists_by_ty[type(i)]
            except KeyError:
                l = item_lists_by_ty[type(i)] = list(self.item_lists_by_ty.get(type(i), ()))
            l.append(i)
        return _KeyRegistryItems(
            self.key,
            (*self.items, *items),
            {**self.item_lists_by_ty, **item_lists_by_ty},
        )


class RegistrySealedError(Exception):
    pass


class Registry(ta.Generic[RegistryItemT]):
    def __init__(
            self,
            *,
            lock: ta.Optional[threading.RLock] = None,  # noqa
    ) -> None:
        super().__init__()

        if lock is None:
            lock = threading.RLock()
        self._lock = lock

        self._state: Registry._State[RegistryItemT] = Registry._State(
            dct={},
            id_dct={},
            version=0,
        )

        self._sealed = False

    #

    @dc.dataclass(frozen=True, kw_only=True)
    class _State(ta.Generic[RegistryItemU]):
        dct: ta.Mapping[ta.Any, _KeyRegistryItems[RegistryItemU]]
        id_dct: ta.Mapping[ta.Any, _KeyRegistryItems[RegistryItemU]]
        version: int

        def register(
                self,
                key: ta.Any,
                *items: RegistryItemT,
                identity: bool = False,
        ) -> 'Registry._State[RegistryItemU]':
            if not items:
                return self

            dct: ta.Any = self.dct if not identity else self.id_dct
            if (sr := dct.get(key)) is None:
                sr = _KeyRegistryItems(key)
            sr.add(*items)

            return Registry._State(
                dct={**self.dct, **dct} if not identity else self.dct,
                id_dct={**self.id_dct, **dct} if identity else self.id_dct,
                version=self.version + 1,
            )

        _get_cache: dict[ta.Any, ta.Sequence[RegistryItem]] = dc.field(default_factory=dict)

        def get(
                self,
                key: ta.Any,
                *,
                identity: bool | None = None,
        ) -> ta.Sequence[RegistryItem]:
            if identity is None:
                try:
                    return self._get_cache[key]
                except KeyError:
                    pass

                ret = self._get_cache[key] = (
                    *self.get(key, identity=True),
                    *self.get(key, identity=False),
                )
                return ret

            dct: ta.Any = self.dct if not identity else self.id_dct
            try:
                return dct[key].items
            except KeyError:
                return ()

        _get_of_cache: dict[ta.Any, dict[type, ta.Sequence[RegistryItem]]] = dc.field(default_factory=dict)

        def get_of(
                self,
                key: ta.Any,
                item_ty: type[RegistryItem],
                *,
                identity: bool | None = None,
        ) -> ta.Sequence[RegistryItem]:
            if identity is None:
                try:
                    return self._get_of_cache[key][item_ty]
                except KeyError:
                    pass

                ret = self._get_of_cache.setdefault(key, {})[item_ty] = (
                    *self.get_of(key, item_ty, identity=True),
                    *self.get_of(key, item_ty, identity=False),
                )
                return ret

            dct: ta.Any = self.dct if not identity else self.id_dct
            try:
                sr = dct[key]
            except KeyError:
                return ()
            return sr.item_lists_by_ty.get(item_ty, ())

    def is_sealed(self) -> bool:
        if self._sealed:
            return True
        with self._lock:
            return self._sealed

    def seal(self) -> ta.Self:
        if self._sealed:
            raise RegistrySealedError(self)
        with self._lock:
            self._seal()
        return self

    def _seal(self) -> None:
        if self._sealed:
            raise RegistrySealedError(self)

        self._sealed = True

    #

    def register(
            self,
            key: ta.Any,
            *items: RegistryItemT,
            identity: bool = False,
    ) -> ta.Self:
        if not items:
            return self

        with self._lock:
            if self._sealed:
                raise RegistrySealedError(self)

            self._state = self._state.register(
                key,
                *items,
                identity=identity,
            )

        return self

    #

    def get(
            self,
            key: ta.Any,
            *,
            identity: bool | None = None,
    ) -> ta.Sequence[RegistryItem]:
        return self._state.get(key, identity=identity)

    def get_of(
            self,
            key: ta.Any,
            item_ty: type[RegistryItemU],
            *,
            identity: bool | None = None,
    ) -> ta.Sequence[RegistryItemU]:
        return self._state.get_of(key, item_ty, identity=identity)
