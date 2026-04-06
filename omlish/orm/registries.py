# ruff: noqa: SLF001
import typing as ta

from .. import check
from .. import collections as col
from .fields import Field
from .mappers import Mapper


##


class Registry:
    def __init__(
            self,
            mappers: ta.Iterable[Mapper],
    ) -> None:
        super().__init__()

        self._mappers: set[Mapper] = set()

        self._mappers_by_cls: dict[type, Mapper] = {}
        self._mappers_by_cls_name: dict[str, Mapper] = {}
        self._mappers_by_store_name: dict[str, Mapper] = {}

        self._fields_by_backref_binding: ta.MutableMapping[ta.Any, Field] = col.IdentityKeyDict()

        self.register(*mappers)

    @property
    def mappers(self) -> ta.AbstractSet[Mapper]:
        return self._mappers

    @property
    def mappers_by_cls(self) -> ta.Mapping[type, Mapper]:
        return self._mappers_by_cls

    @property
    def mappers_by_cls_name(self) -> ta.Mapping[str, Mapper]:
        return self._mappers_by_cls_name

    @property
    def mappers_by_store_name(self) -> ta.Mapping[str, Mapper]:
        return self._mappers_by_store_name

    #

    def _check_can_register(self, m: Mapper) -> None:
        check.not_in(m, self._mappers)
        check.not_in(m.cls, self._mappers_by_cls)
        check.not_in(m.cls.__name__, self._mappers_by_cls_name)
        check.not_in(m.store_name, self._mappers_by_store_name)
        for f in m.fields:
            if (fbb := f.backref_binding) is not None:
                check.not_in(fbb, self._fields_by_backref_binding)

    def _register(self, m: Mapper) -> None:
        self._check_can_register(m)

        m._set_registry(self)

        self._mappers.add(m)
        self._mappers_by_cls[m.cls] = m
        self._mappers_by_cls_name[m.cls.__name__] = m
        self._mappers_by_store_name[m.store_name] = m
        for f in m.fields:
            if (fbb := f.backref_binding) is not None:
                self._fields_by_backref_binding[fbb] = f

    def register(self, *mappers: Mapper) -> None:
        for m in mappers:
            self._register(m)

    #

    def mapper_for_cls(self, cls: type) -> Mapper:
        return self._mappers_by_cls[cls]

    def mapper_for_obj(self, obj: ta.Any) -> Mapper:
        return self.mapper_for_cls(type(obj))

    #

    # def field_for_backref(self, br: Backref):
