"""
TODO:
 - col.TypeMap?
  - at least get_any
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
    items: list[RegistryItemT] = dc.field(default_factory=list)
    item_lists_by_ty: dict[type[RegistryItemT], list[RegistryItemT]] = dc.field(default_factory=dict)

    def add(self, *items: RegistryItemT) -> None:
        for i in items:
            self.items.append(i)
            self.item_lists_by_ty.setdefault(type(i), []).append(i)


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

        self._dct: dict[ta.Any, _KeyRegistryItems[RegistryItemT]] = {}
        self._id_dct: ta.MutableMapping[ta.Any, _KeyRegistryItems[RegistryItemT]] = col.IdentityKeyDict()

        self._version = 0
        self._sealed = False

    #

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

            dct: ta.Any = self._id_dct if identity else self._dct
            if (sr := dct.get(key)) is None:
                sr = dct[key] = _KeyRegistryItems(key)
            sr.add(*items)

            self._version += 1

        return self

    #

    def get(
            self,
            key: ta.Any,
            *,
            identity: bool | None = None,
    ) -> ta.Sequence[RegistryItem]:
        if identity is None:
            return (
                *self.get(key, identity=True),
                *self.get(key, identity=False),
            )

        dct: ta.Any = self._id_dct if identity else self._dct
        try:
            return dct[key].items
        except KeyError:
            return ()

    def get_of(
            self,
            key: ta.Any,
            item_ty: type[RegistryItemU],
            *,
            identity: bool | None = None,
    ) -> ta.Sequence[RegistryItemU]:
        if identity is None:
            return (
                *self.get_of(key, item_ty, identity=True),
                *self.get_of(key, item_ty, identity=False),
            )

        dct: ta.Any = self._id_dct if identity else self._dct
        try:
            sr = dct[key]
        except KeyError:
            return ()
        return sr.item_lists_by_ty.get(item_ty, ())
