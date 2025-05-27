import dataclasses as dc
import types
import typing as ta

from omlish import check
from omlish import lang
from omlish import reflect as rfl


##


@dc.dataclass(frozen=True)
class ToolDtype(lang.Abstract, lang.Sealed):
    pass


#


@dc.dataclass(frozen=True)
class PrimitiveToolDtype(ToolDtype):
    type: str


OBJECT_PRIMITIVE_TYPE = PrimitiveToolDtype('object')

NULL_PRIMITIVE_TYPE = PrimitiveToolDtype('null')

PRIMITIVE_TYPE_MAP: ta.Mapping[rfl.Type, ToolDtype] = {
    int: PrimitiveToolDtype('integer'),
    float: PrimitiveToolDtype('number'),
    str: PrimitiveToolDtype('string'),
    bool: PrimitiveToolDtype('boolean'),
    types.NoneType: NULL_PRIMITIVE_TYPE,

    rfl.type_(ta.Any): PrimitiveToolDtype('any'),
}


#


@dc.dataclass(frozen=True)
class UnionToolDtype(ToolDtype):
    args: ta.Sequence[ToolDtype]

    def __post_init__(self) -> None:
        check.arg(len(self.args) > 1)
        check.unique(self.args)
        check.not_in(NULL_PRIMITIVE_TYPE, self.args)


@dc.dataclass(frozen=True)
class NullableToolDtype(ToolDtype):
    type: ToolDtype


#


@dc.dataclass(frozen=True)
class SequenceToolDtype(ToolDtype):
    element: ToolDtype


@dc.dataclass(frozen=True)
class MappingToolDtype(ToolDtype):
    key: ToolDtype
    value: ToolDtype


@dc.dataclass(frozen=True)
class TupleToolDtype(ToolDtype):
    elements: ta.Sequence[ToolDtype]


#


@dc.dataclass(frozen=True)
class EnumToolDtype(ToolDtype):
    type: ToolDtype
    values: ta.Sequence[ta.Any]


##


@dc.dataclass(frozen=True)
class ToolParam:
    name: str

    _: dc.KW_ONLY

    desc: str | None = None

    type: ToolDtype | None = None

    required: bool = False


##


@dc.dataclass(frozen=True)
class ToolSpec:
    name: str

    _: dc.KW_ONLY

    desc: str | None = None

    params: ta.Sequence[ToolParam] | None = None
    allow_additional_params: bool = False

    returns_desc: str | None = None
    returns_type: ToolDtype | None = None


##


@dc.dataclass(frozen=True)
class ToolExecRequest(lang.Final):
    id: str
    spec: ToolSpec
    args: ta.Mapping[str, ta.Any]

    _: dc.KW_ONLY

    raw_args: str | None = None
