import abc
import dataclasses as dc
import threading
import typing as ta

from .. import check
from .specs import SPEC_TYPES
from .specs import Spec


class RegistryItem(abc.ABC):
    pass


RegistryItemT = ta.TypeVar('RegistryItemT', bound=RegistryItem)


@dc.dataclass(frozen=True)
class _SpecRegistry:
    spec: Spec
    items: list[RegistryItem] = dc.field(default_factory=list)
    item_lists_by_ty: dict[ta.Type[RegistryItem], list[RegistryItem]] = dc.field(default_factory=dict)

    def add(self, *items: RegistryItem) -> None:
        for i in items:
            self.items.append(i)
            self.item_lists_by_ty.setdefault(type(i), []).append(i)


class Registry:
    def __init__(self) -> None:
        super().__init__()
        self._mtx = threading.Lock()
        self._dct: dict[Spec, _SpecRegistry] = {}
        self._ps: ta.Sequence['Registry'] = []

    def register(self, spec: Spec, *items: RegistryItem) -> 'Registry':
        check.isinstance(spec, SPEC_TYPES)
        with self._mtx:
            if (sr := self._dct.get(spec)) is None:
                sr = self._dct[spec] = _SpecRegistry(spec)
            sr.add(*items)
        return self

    def get(self, spec: Spec) -> ta.Sequence[RegistryItem]:
        check.isinstance(spec, SPEC_TYPES)
        try:
            return self._dct[spec].items
        except KeyError:
            return ()

    def get_of(self, spec: Spec, item_ty: ta.Type[RegistryItemT]) -> ta.Sequence[RegistryItemT]:
        check.isinstance(spec, SPEC_TYPES)
        try:
            sr = self._dct[spec]
        except KeyError:
            return ()
        return sr.item_lists_by_ty.get(item_ty, ())  # type: ignore
