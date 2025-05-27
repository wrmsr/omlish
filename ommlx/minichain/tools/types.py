import operator
import types
import typing as ta

from omlish import cached
from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl


##


@dc.dataclass(frozen=True)
class ToolDtype(lang.Abstract, lang.Sealed):
    @classmethod
    def of(cls, obj: ta.Any) -> 'ToolDtype':
        """Only supports the simplest cases - use reflection by default."""

        if isinstance(obj, ToolDtype):
            return obj

        elif isinstance(obj, str):
            return PrimitiveToolDtype(obj)

        else:
            return PrimitiveToolDtype.of(obj)


#


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class PrimitiveToolDtype(ToolDtype):
    type: str

    def __post_init__(self) -> None:
        check.non_empty_str(self.type)

    @classmethod
    def of(cls, obj: ta.Any) -> 'PrimitiveToolDtype':
        if isinstance(obj, PrimitiveToolDtype):
            return obj

        rty = rfl.type_(obj)

        if isinstance(rty, (type, rfl.Any)):
            return PRIMITIVE_TOOL_DTYPE_MAP.get(rty, OBJECT_PRIMITIVE_TOOL_DTYPE)

        else:
            raise TypeError(rty)


OBJECT_PRIMITIVE_TOOL_DTYPE = PrimitiveToolDtype('object')

NULL_PRIMITIVE_TOOL_DTYPE = PrimitiveToolDtype('null')

PRIMITIVE_TOOL_DTYPE_MAP: ta.Mapping[rfl.Type, PrimitiveToolDtype] = {
    int: PrimitiveToolDtype('integer'),
    float: PrimitiveToolDtype('number'),
    str: PrimitiveToolDtype('string'),
    bool: PrimitiveToolDtype('boolean'),
    types.NoneType: NULL_PRIMITIVE_TOOL_DTYPE,

    rfl.type_(ta.Any): PrimitiveToolDtype('any'),
}


#


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class UnionToolDtype(ToolDtype):
    args: ta.Sequence[ToolDtype]

    def __post_init__(self) -> None:
        check.arg(len(self.args) > 1)
        check.unique(self.args)
        check.not_in(NULL_PRIMITIVE_TOOL_DTYPE, self.args)


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class NullableToolDtype(ToolDtype):
    type: ToolDtype


#


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class SequenceToolDtype(ToolDtype):
    element: ToolDtype


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class MappingToolDtype(ToolDtype):
    key: ToolDtype
    value: ToolDtype


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class TupleToolDtype(ToolDtype):
    elements: ta.Sequence[ToolDtype]


#


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class EnumToolDtype(ToolDtype):
    type: ToolDtype
    values: ta.Sequence[ta.Any]


##


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['desc', 'type'], omit_if=lang.is_none)
@msh.update_fields_metadata(['required'], omit_if=operator.not_)
class ToolParam:
    name: str

    _: dc.KW_ONLY

    desc: str | None = None

    type: ToolDtype | None = None

    required: bool = False

    #

    def __post_init__(self) -> None:
        check.non_empty_str(self.name)


##


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['desc', 'params', 'returns_desc', 'returns_type'], omit_if=lang.is_none)
@msh.update_fields_metadata(['allow_additional_params'], omit_if=operator.not_)
class ToolSpec:
    name: str

    _: dc.KW_ONLY

    desc: str | None = None

    params: ta.Sequence[ToolParam] | None = None
    allow_additional_params: bool = False

    returns_desc: str | None = None
    returns_type: ToolDtype | None = None

    #

    def __post_init__(self) -> None:
        check.non_empty_str(self.name)

    @cached.property
    @dc.init
    def params_by_name(self) -> ta.Mapping[str, ToolParam]:
        return col.make_map_by(
            lambda p: p.name,
            self.params or [],
            strict=True,
        )


##


@dc.dataclass(frozen=True)
class ToolExecRequest(lang.Final):
    id: str
    spec: ToolSpec
    args: ta.Mapping[str, ta.Any]

    _: dc.KW_ONLY

    raw_args: str | None = None
