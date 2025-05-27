import dataclasses as dc
import types
import typing as ta

from omlish import check
from omlish import lang
from omlish import reflect as rfl


##


@dc.dataclass(frozen=True)
class Type(lang.Abstract, lang.Sealed):
    pass


#


@dc.dataclass(frozen=True)
class Primitive(Type):
    type: str


OBJECT_PRIMITIVE_TYPE = Primitive('object')

NULL_PRIMITIVE_TYPE = Primitive('null')

PRIMITIVE_TYPE_MAP: ta.Mapping[rfl.Type, Type] = {
    int: Primitive('integer'),
    float: Primitive('number'),
    str: Primitive('string'),
    bool: Primitive('boolean'),
    types.NoneType: NULL_PRIMITIVE_TYPE,

    rfl.type_(ta.Any): Primitive('any'),
}


#


@dc.dataclass(frozen=True)
class Union(Type):
    args: ta.Sequence[Type]

    def __post_init__(self) -> None:
        check.arg(len(self.args) > 1)
        check.unique(self.args)
        check.not_in(NULL_PRIMITIVE_TYPE, self.args)


@dc.dataclass(frozen=True)
class Nullable(Type):
    type: Type


#


@dc.dataclass(frozen=True)
class Sequence(Type):
    element: Type


@dc.dataclass(frozen=True)
class Mapping(Type):
    key: Type
    value: Type


@dc.dataclass(frozen=True)
class Tuple(Type):
    elements: ta.Sequence[Type]


#


@dc.dataclass(frozen=True)
class Enum(Type):
    type: Type
    values: ta.Sequence[ta.Any]


##


@dc.dataclass(frozen=True)
class Param:
    name: str

    _: dc.KW_ONLY

    description: str | None = None

    type: Type | None = None

    required: bool = False


##


@dc.dataclass(frozen=True)
class Function:
    name: str

    _: dc.KW_ONLY

    description: str | None = None

    params: ta.Sequence[Param] | None = None

    returns_description: str | None = None
    returns_type: Type | None = None
