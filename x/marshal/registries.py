import abc
import dataclasses as dc
import threading
import typing as ta

from .specs import Spec


class RegistryItem(abc.ABC):
    pass


RegistryItemT = ta.TypeVar('RegistryItemT', bound=RegistryItem)


@dc.dataclass(frozen=True)
class _SpecRegistry:
    spec: Spec
    items: ta.List[RegistryItem] = dc.field(default_factory=list)
    item_lists_by_ty: ta.Dict[ta.Type[RegistryItem], ta.List[RegistryItem]] = dc.field(default_factory=dict)

    def add(self, *items: RegistryItem) -> None:
        for i in items:
            self.items.append(i)
            self.item_lists_by_ty.setdefault(type(i), []).append(i)


class Registry:
    def __init__(self) -> None:
        super().__init__()
        self._mtx = threading.Lock()
        self._dct: ta.Dict[Spec, _SpecRegistry] = {}
        self._ps: ta.Sequence['Registry'] = []

    def register(self, ty: Spec, *items: RegistryItem) -> None:
        with self._mtx:
            if (tr := self._dct.get(ty)):
                tr = self._dct[ty] = _SpecRegistry(ty)
            tr.add(*items)

    def get(self, ty: Spec) -> ta.Sequence[RegistryItem]:
        try:
            return self._dct[ty].items
        except KeyError:
            return ()

    def get_of(self, ty: Spec, item_ty: ta.Type[RegistryItemT]) -> ta.Sequence[RegistryItemT]:
        try:
            tr = self._dct[ty]
        except KeyError:
            return ()
        return tr.item_lists_by_ty.get(item_ty, ())
