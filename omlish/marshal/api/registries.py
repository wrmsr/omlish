"""
TODO:
 - col.TypeMap?
  - at least get_any
"""
import abc
import dataclasses as dc
import threading
import typing as ta

from ... import lang


##


class RegistryItem(lang.Abstract):
    pass


RegistryItemT = ta.TypeVar('RegistryItemT', bound=RegistryItem)
RegistryItemU = ta.TypeVar('RegistryItemU', bound=RegistryItem)


##


class RegistryView(lang.Abstract, ta.Generic[RegistryItemT]):
    @abc.abstractmethod
    def get(
            self,
            key: ta.Any,
            *,
            identity: bool | None = None,
    ) -> ta.Sequence[RegistryItemT]:
        ...

    @abc.abstractmethod
    def get_of(
            self,
            key: ta.Any,
            item_ty: type[RegistryItemU],
            *,
            identity: bool | None = None,
    ) -> ta.Sequence[RegistryItemU]:
        ...


##


class RegistrySealedError(Exception):
    pass


class Registry(RegistryView[RegistryItemT]):
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

    @dc.dataclass(frozen=True)
    class _KeyItems(ta.Generic[RegistryItemU]):
        key: ta.Any
        items: ta.Sequence[RegistryItemU] = ()
        item_lists_by_ty: ta.Mapping[type[RegistryItemU], ta.Sequence[RegistryItemU]] = dc.field(default_factory=dict)

        def add(self, *items: RegistryItemU) -> 'Registry._KeyItems[RegistryItemU]':
            item_lists_by_ty: dict[type[RegistryItemU], list[RegistryItemU]] = {}

            for i in items:
                try:
                    l = item_lists_by_ty[type(i)]
                except KeyError:
                    l = item_lists_by_ty[type(i)] = list(self.item_lists_by_ty.get(type(i), ()))
                l.append(i)

            return Registry._KeyItems(
                self.key,
                (*self.items, *items),
                {**self.item_lists_by_ty, **item_lists_by_ty},
            )

    @dc.dataclass(frozen=True, kw_only=True)
    class _State(ta.Generic[RegistryItemU]):
        dct: ta.Mapping[ta.Any, 'Registry._KeyItems[RegistryItemU]']
        id_dct: ta.Mapping[ta.Any, 'Registry._KeyItems[RegistryItemU]']
        version: int

        #

        def register(
                self,
                key: ta.Any,
                *items: RegistryItemT,
                identity: bool = False,
        ) -> 'Registry._State[RegistryItemU]':
            if not items:
                return self

            sr_dct: ta.Any = self.dct if not identity else self.id_dct
            if (sr := sr_dct.get(key)) is None:
                sr = Registry._KeyItems(key)
            sr = sr.add(*items)
            new = {key: sr}

            return Registry._State(
                dct={**self.dct, **new} if not identity else self.dct,
                id_dct={**self.id_dct, **new} if identity else self.id_dct,
                version=self.version + 1,
            )

        #

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
    ) -> ta.Sequence[RegistryItemT]:
        return self._state.get(key, identity=identity)  # type: ignore [return-value]

    def get_of(
            self,
            key: ta.Any,
            item_ty: type[RegistryItemU],
            *,
            identity: bool | None = None,
    ) -> ta.Sequence[RegistryItemU]:
        return self._state.get_of(key, item_ty, identity=identity)  # type: ignore [return-value]
