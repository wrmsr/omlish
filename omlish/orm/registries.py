# ruff: noqa: SLF001
import typing as ta

from .. import check
from .codecs import Codec
from .mappers import Mapper


##


class Registry:
    def __init__(
            self,
            mappers: ta.Iterable[Mapper],
            *,
            codec: Codec | None = None,
    ) -> None:
        super().__init__()

        self._codec = codec

        self._mappers: set[Mapper] = set()

        self._mappers_by_cls: dict[type, Mapper] = {}
        self._mappers_by_cls_name: dict[str, Mapper] = {}
        self._mappers_by_store_name: dict[str, Mapper] = {}

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

    @property
    def codec(self) -> Codec | None:
        return self._codec

    #

    def _check_can_register(self, m: Mapper) -> None:
        check.not_in(m, self._mappers)
        check.not_in(m.cls, self._mappers_by_cls)
        check.not_in(m.cls.__name__, self._mappers_by_cls_name)
        check.not_in(m.store_name, self._mappers_by_store_name)

    def _register(self, m: Mapper) -> None:
        self._check_can_register(m)

        m._set_registry(self)

        self._mappers.add(m)
        self._mappers_by_cls[m.cls] = m
        self._mappers_by_cls_name[m.cls.__name__] = m
        self._mappers_by_store_name[m.store_name] = m

    def register(self, *mappers: Mapper) -> None:
        for m in mappers:
            self._register(m)

    #

    def mapper_for_cls(self, cls: type) -> Mapper:
        return self._mappers_by_cls[cls]

    def mapper_for_obj(self, obj: ta.Any) -> Mapper:
        return self.mapper_for_cls(type(obj))
