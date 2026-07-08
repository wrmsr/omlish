import operator
import types
import typing as ta

from omlish import cached
from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish import reflect2 as rfl

from ..content.content import Content
from ..metadata import MetadataContainerDataclass
from .metadata import ToolUseMetadatas
from .metadata import ToolUseResultMetadatas


msh.register_global_module_import('._marshal', __package__)


##


@dc.dataclass(frozen=True)
class ToolDtype(lang.Abstract, lang.Sealed):
    @classmethod
    def of(cls, obj: ta.Any) -> ToolDtype:
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
    def of(cls, obj: ta.Any) -> PrimitiveToolDtype:
        if isinstance(obj, PrimitiveToolDtype):
            return obj

        rty = rfl.reflect_type(obj)

        if isinstance(rty, rfl.AnyType):
            return PRIMITIVE_TOOL_DTYPE_MAP[ta.Any]

        if (pty := rfl.get_runtime_type_or_none(rty)) is not None:
            return PRIMITIVE_TOOL_DTYPE_MAP.get(pty, OBJECT_PRIMITIVE_TOOL_DTYPE)

        raise TypeError(rty)


OBJECT_PRIMITIVE_TOOL_DTYPE = PrimitiveToolDtype('object')

NULL_PRIMITIVE_TOOL_DTYPE = PrimitiveToolDtype('null')

PRIMITIVE_TOOL_DTYPE_MAP: ta.Mapping[ta.Any, PrimitiveToolDtype] = {
    int: PrimitiveToolDtype('integer'),
    float: PrimitiveToolDtype('number'),
    str: PrimitiveToolDtype('string'),
    bool: PrimitiveToolDtype('boolean'),
    types.NoneType: NULL_PRIMITIVE_TOOL_DTYPE,

    ta.Any: PrimitiveToolDtype('any'),
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


#


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class ObjectToolDtype(ToolDtype):
    fields: ta.Mapping[str, ToolDtype]


##


@dc.dataclass(frozen=True)
@msh.update_field_options(['name', 'desc', 'type'], omit_if=lang.is_none)
@msh.update_field_options('required', omit_if=operator.not_)
class ToolParam:
    name: str | None = None

    _: dc.KW_ONLY

    desc: Content | None = None

    type: ToolDtype | None = None

    required: bool | None = None


##


@dc.dataclass(frozen=True)
@msh.update_field_options(['name', 'desc', 'params', 'returns_desc', 'returns_type'], omit_if=lang.is_none)
@msh.update_field_options('allow_additional_params', omit_if=operator.not_)
class ToolSpec:
    name: str | None = None

    _: dc.KW_ONLY

    desc: Content | None = None

    params: ta.Sequence[ToolParam] | None = None
    allow_additional_params: bool | None = None

    returns_desc: Content | None = None
    returns_type: ToolDtype | None = None

    @cached.property
    def params_by_name(self) -> ta.Mapping[str, ToolParam]:
        return col.make_map_by(
            lambda p: check.non_empty_str(p.name),
            self.params or [],
            strict=True,
        )


##


@dc.dataclass(frozen=True, kw_only=True)
class ToolUse(MetadataContainerDataclass[ToolUseMetadatas], lang.Final):
    id: str | None = None
    name: str
    args: ta.Mapping[str, ta.Any]

    raw_args: str | None = None

    #

    _metadata: ta.Sequence[ToolUseMetadatas] = dc.field(default=(), kw_only=True, repr=False)

    MetadataContainerDataclass._configure_metadata_field(_metadata, ToolUseMetadatas)  # noqa


@dc.dataclass(frozen=True, kw_only=True)
class ToolUseResult(MetadataContainerDataclass[ToolUseResultMetadatas], lang.Final):
    id: str | None = None
    name: str
    c: Content

    #

    _metadata: ta.Sequence[ToolUseResultMetadatas] = dc.field(default=(), kw_only=True, repr=False)

    MetadataContainerDataclass._configure_metadata_field(_metadata, ToolUseResultMetadatas)  # noqa
