import dataclasses as dc
import threading
import typing as ta

from .. import lang


class RegistryItem(lang.Abstract):
    pass


HashableT = ta.TypeVar('HashableT', bound=ta.Hashable)
RegistryItemT = ta.TypeVar('RegistryItemT', bound=RegistryItem)


@dc.dataclass(frozen=True)
class _KeyRegistryItems:
    key: ta.Hashable
    items: list[RegistryItem] = dc.field(default_factory=list)
    item_lists_by_ty: dict[type[RegistryItem], list[RegistryItem]] = dc.field(default_factory=dict)

    def add(self, *items: RegistryItem) -> None:
        for i in items:
            self.items.append(i)
            self.item_lists_by_ty.setdefault(type(i), []).append(i)


class Registry(ta.Generic[HashableT]):
    def __init__(self) -> None:
        super().__init__()
        self._mtx = threading.Lock()
        self._dct: dict[HashableT, _KeyRegistryItems] = {}
        self._ps: ta.Sequence[Registry] = []

    def register(self, key: HashableT, *items: RegistryItem) -> 'Registry':
        with self._mtx:
            if (sr := self._dct.get(key)) is None:
                sr = self._dct[key] = _KeyRegistryItems(key)
            sr.add(*items)
        return self

    def get(self, key: HashableT) -> ta.Sequence[RegistryItem]:
        try:
            return self._dct[key].items
        except KeyError:
            return ()

    def get_of(self, key: HashableT, item_ty: type[RegistryItemT]) -> ta.Sequence[RegistryItemT]:
        try:
            sr = self._dct[key]
        except KeyError:
            return ()
        return sr.item_lists_by_ty.get(item_ty, ())  # type: ignore
