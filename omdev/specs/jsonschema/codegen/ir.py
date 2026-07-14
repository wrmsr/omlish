import typing as ta

from omcore import dataclasses as dc
from omcore import lang


##
# Type references


class TypeRef(lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class PrimitiveTypeRef(TypeRef, lang.Final):
    python_type: str


@dc.dataclass(frozen=True)
class LiteralTypeRef(TypeRef, lang.Final):
    values: ta.Sequence[ta.Any]


@dc.dataclass(frozen=True)
class RefTypeRef(TypeRef, lang.Final):
    name: str


@dc.dataclass(frozen=True)
class ArrayTypeRef(TypeRef, lang.Final):
    item: TypeRef


@dc.dataclass(frozen=True)
class NullableTypeRef(TypeRef, lang.Final):
    inner: TypeRef


class AnyTypeRef(TypeRef, lang.Final):
    pass


@dc.dataclass(frozen=True)
class MapTypeRef(TypeRef, lang.Final):
    value: TypeRef | None = None


@dc.dataclass(frozen=True)
class UnionTypeRef(TypeRef, lang.Final):
    members: ta.Sequence[TypeRef]


##
# Definitions


MISSING: ta.Any = object()


@dc.dataclass(frozen=True, kw_only=True)
class FieldDef(lang.Final):
    json_name: str
    python_name: str
    type_ref: TypeRef
    required: bool
    default: ta.Any = MISSING
    const: ta.Any = MISSING


@dc.dataclass(frozen=True, kw_only=True)
class ObjectTypeDef(lang.Final):
    name: str
    fields: ta.Sequence[FieldDef] = ()
    nested_defs: ta.Sequence[ObjectTypeDef] = ()
    field_naming: str | None = None
    ignore_unknown: bool = False


@dc.dataclass(frozen=True, kw_only=True)
class StringEnumTypeDef(lang.Final):
    name: str
    values: ta.Sequence[str] = ()


@dc.dataclass(frozen=True, kw_only=True)
class DiscriminatedUnionVariant(lang.Final):
    tag_value: str
    ref_name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class DiscriminatedUnionTypeDef(lang.Final):
    name: str
    discriminator_field: str = ''
    variants: ta.Sequence[DiscriminatedUnionVariant] = ()


@dc.dataclass(frozen=True, kw_only=True)
class AnyOfUnionTypeDef(lang.Final):
    name: str
    members: ta.Sequence[TypeRef] = ()


@dc.dataclass(frozen=True, kw_only=True)
class AllOfIntersectionTypeDef(lang.Final):
    name: str
    members: ta.Sequence[ta.Any] = ()


@dc.dataclass(frozen=True, kw_only=True)
class TypeAliasTypeDef(lang.Final):
    name: str
    target: TypeRef | None = None


@dc.dataclass(frozen=True, kw_only=True)
class EmptyTypeDef(lang.Final):
    name: str


TypeDef: ta.TypeAlias = ta.Union[  # noqa
    ObjectTypeDef,
    StringEnumTypeDef,
    DiscriminatedUnionTypeDef,
    AnyOfUnionTypeDef,
    AllOfIntersectionTypeDef,
    TypeAliasTypeDef,
    EmptyTypeDef,
]

TYPE_DEF_TYPES: tuple[type, ...] = (
    ObjectTypeDef,
    StringEnumTypeDef,
    DiscriminatedUnionTypeDef,
    AnyOfUnionTypeDef,
    AllOfIntersectionTypeDef,
    TypeAliasTypeDef,
    EmptyTypeDef,
)


##


@dc.dataclass(frozen=True, kw_only=True)
class VariantWrapperDef(lang.Final):
    class_name: str
    union_name: str
    tag_field_json: str
    tag_field_python: str
    tag_value: str
    source_fields: ta.Sequence[FieldDef] = ()


@dc.dataclass(frozen=True, kw_only=True)
class ModuleDef(lang.Final):
    type_defs: ta.Mapping[str, TypeDef]
    disc_unions: ta.Mapping[str, DiscriminatedUnionTypeDef]
    variant_wrappers: ta.Sequence[VariantWrapperDef]
