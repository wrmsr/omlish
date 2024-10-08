"""
TODO:
 - inheritance
"""
import dataclasses as dc
import threading
import typing as ta

from .. import collections as col
from .. import lang


class RegistryItem(lang.Abstract):
    pass


RegistryItemT = ta.TypeVar('RegistryItemT', bound=RegistryItem)


@dc.dataclass(frozen=True)
class _KeyRegistryItems:
    key: ta.Any
    items: list[RegistryItem] = dc.field(default_factory=list)
    item_lists_by_ty: dict[type[RegistryItem], list[RegistryItem]] = dc.field(default_factory=dict)

    def add(self, *items: RegistryItem) -> None:
        for i in items:
            self.items.append(i)
            self.item_lists_by_ty.setdefault(type(i), []).append(i)


class Registry:
    def __init__(self) -> None:
        super().__init__()
        self._mtx = threading.Lock()
        self._idct: ta.MutableMapping[ta.Any, _KeyRegistryItems] = col.IdentityKeyDict()
        self._dct: dict[ta.Any, _KeyRegistryItems] = {}

    def register(
            self,
            key: ta.Any,
            *items: RegistryItem,
            identity: bool = False,
    ) -> 'Registry':
        with self._mtx:
            dct: ta.Any = self._idct if identity else self._dct
            if (sr := dct.get(key)) is None:
                sr = dct[key] = _KeyRegistryItems(key)
            sr.add(*items)
        return self

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
        dct: ta.Any = self._idct if identity else self._dct
        try:
            return dct[key].items
        except KeyError:
            return ()

    def get_of(
            self,
            key: ta.Any,
            item_ty: type[RegistryItemT],
            *,
            identity: bool | None = None,
    ) -> ta.Sequence[RegistryItemT]:
        if identity is None:
            return (
                *self.get_of(key, item_ty, identity=True),
                *self.get_of(key, item_ty, identity=False),
            )
        dct: ta.Any = self._idct if identity else self._dct
        try:
            sr = dct[key]
        except KeyError:
            return ()
        return sr.item_lists_by_ty.get(item_ty, ())
