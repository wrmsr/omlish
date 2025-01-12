import abc
import typing as ta

from omlish import cached
from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang


DateTime = ta.NewType('DateTime', str)
MillisecondDateTime = ta.NewType('MillisecondDateTime', str)

Timestamp = ta.NewType('Timestamp', str)


##


@dc.dataclass(frozen=True)
class Tag:
    key: str
    value: str


TagList: ta.TypeAlias = ta.Sequence[Tag]


##


class ValueType(abc.ABC):  # noqa
    pass


@dc.dataclass(frozen=True)
class ListValueType(ValueType):
    e: type


@dc.dataclass(frozen=True)
class MapValueType(ValueType):
    k: type
    v: type


##


class SHAPE_NAME(lang.Marker):  # noqa
    pass


def common_metadata(
        *,
        shape_name: str | None = None,
) -> dict[ta.Any, ta.Any]:
    md = {}

    if shape_name is not None:
        md[SHAPE_NAME] = shape_name

    return md


##


def shape_metadata(
        **kwargs: ta.Any,
) -> dict[ta.Any, ta.Any]:
    md = {**common_metadata(**kwargs)}

    return md


class ShapeInfo:
    def __init__(
            self,
            cls: type['Shape'],
            metadata: ta.Mapping[ta.Any, ta.Any],
    ) -> None:
        super().__init__()

        self._cls = check.issubclass(cls, Shape)
        self._metadata = metadata

    @property
    def cls(self) -> type['Shape']:
        return self._cls

    @property
    def metadata(self) -> ta.Mapping[ta.Any, ta.Any]:
        return self._metadata

    #

    @cached.property
    def fields(self) -> ta.Sequence[dc.Field]:
        check.state(dc.is_immediate_dataclass(self._cls))
        fls = dc.fields(self._cls)
        return fls  # noqa

    @cached.property
    def fields_by_name(self) -> ta.Mapping[str, dc.Field]:
        return col.make_map_by(lambda fl: fl.name, self.fields, strict=True)

    @cached.property
    def fields_by_member_name(self) -> ta.Mapping[str, dc.Field]:
        return col.make_map(
            [(n, f) for f in self.fields if (n := f.metadata.get(MEMBER_NAME)) is not None],
            strict=True,
        )

    @cached.property
    def fields_by_serialization_name(self) -> ta.Mapping[str, dc.Field]:
        l = []
        for f in self.fields:
            if sn := f.metadata.get(SERIALIZATION_NAME):
                l.append((sn, f))
            elif mn := f.metadata.get(MEMBER_NAME):
                l.append((mn, f))
        return col.make_map(l, strict=True)


@dc.dataclass(frozen=True, kw_only=True)
class Shape:
    __shape__: ta.ClassVar[ShapeInfo]

    def __init_subclass__(
            cls,
            *,
            shape_name: str | None = None,
            **kwargs: ta.Any,
    ) -> None:
        super().__init_subclass__(**kwargs)

        check.state(not hasattr(cls, '__shape__'))

        info = ShapeInfo(
            cls,
            shape_metadata(**kwargs),
        )

        cls.__shape__ = info


##


class MEMBER_NAME(lang.Marker):  # noqa
    pass


class SERIALIZATION_NAME(lang.Marker):  # noqa
    pass


class VALUE_TYPE(lang.Marker):  # noqa
    pass


#


def field_metadata(
        *,
        member_name: str | None = None,
        serialization_name: str | None = None,
        value_type: ValueType | None = None,
        **kwargs: ta.Any,
) -> dict[ta.Any, ta.Any]:
    md = {**common_metadata(**kwargs)}

    if member_name is not None:
        md[MEMBER_NAME] = member_name
    if serialization_name is not None:
        md[SERIALIZATION_NAME] = serialization_name
    if value_type is not None:
        md[VALUE_TYPE] = value_type

    return md


##


@dc.dataclass(frozen=True, eq=False, kw_only=True)
class Operation:
    name: str

    input: type[Shape] | None = None
    output: type[Shape] | None = None

    errors: ta.Sequence[type[Shape]] | None = None
