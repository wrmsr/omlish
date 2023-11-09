import abc
import dataclasses as dc
import threading
import typing as ta

from .. import check
from .. import reflect as rfl


class RegistryItem(abc.ABC):
    pass


RegistryItemT = ta.TypeVar('RegistryItemT', bound=RegistryItem)


@dc.dataclass(frozen=True)
class _TypeRegistry:
    rty: rfl.Type
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
        self._dct: dict[rfl.Type, _TypeRegistry] = {}
        self._ps: ta.Sequence['Registry'] = []

    def register(self, rty: rfl.Type, *items: RegistryItem) -> 'Registry':
        check.isinstance(rty, rfl.TYPES)
        with self._mtx:
            if (sr := self._dct.get(rty)) is None:
                sr = self._dct[rty] = _TypeRegistry(rty)
            sr.add(*items)
        return self

    def get(self, rty: rfl.Type) -> ta.Sequence[RegistryItem]:
        check.isinstance(rty, rfl.TYPES)
        try:
            return self._dct[rty].items
        except KeyError:
            return ()

    def get_of(self, rty: rfl.Type, item_ty: type[RegistryItemT]) -> ta.Sequence[RegistryItemT]:
        check.isinstance(rty, rfl.TYPES)
        try:
            sr = self._dct[rty]
        except KeyError:
            return ()
        return sr.item_lists_by_ty.get(item_ty, ())  # type: ignore
