# ruff: noqa: SLF001
import collections.abc as cabc
import dataclasses as dc
import enum
import typing as ta

from ..core.subtypes import get_base_args
from ..core.typekeys import TypeKey
from ..core.typeops import get_type_alias_target
from ..core.types import AnnotatedType
from ..core.types import AnyType
from ..core.types import Instance
from ..core.types import LiteralType
from ..core.types import LiteralValue
from ..core.types import NoneType
from ..core.types import Type
from ..core.types import TypeAliasType
from ..core.types import UnionType
from ..errors import ReflectionTypeError
from ..reflect import DEFAULT_REFLECTOR
from ..reflect import RuntimeTypeReflector
from ..universe import DEFAULT_UNIVERSE
from ..universe import RuntimeTypeUniverse


##


@dc.dataclass(frozen=True)
class LiteralValueType:
    value_type: type
    values: tuple[LiteralValue, ...]


@dc.dataclass(frozen=True)
class RuntimeLiteralValueType:
    value_type: type
    values: tuple[object, ...]


@dc.dataclass(frozen=True)
class LiteralUnion:
    value_type: type
    literal: Type
    non_literal: Type
    values: tuple[LiteralValue, ...]


@dc.dataclass(frozen=True)
class PrimitiveUnion:
    primitives: tuple[type, ...]
    non_primitives: tuple[Type, ...]


@dc.dataclass(frozen=True)
class RuntimeNewType:
    obj: object
    runtime_supertype: object
    supertype: Type


@dc.dataclass(frozen=True)
class RuntimeAnnotated:
    item: Type
    metadata: tuple[object, ...]


@dc.dataclass(frozen=True)
class RuntimeTypeAlias:
    obj: object | None
    alias: TypeAliasType
    target: Type


@dc.dataclass(frozen=True)
class RuntimeTypeShape:
    original: Type
    annotated: RuntimeAnnotated | None
    unannotated: Type
    alias: RuntimeTypeAlias | None
    unaliased: Type
    new_type: RuntimeNewType | None
    effective: Type
    optional_item: Type | None
    literal_value_type: LiteralValueType | None
    literal_union: LiteralUnion | None
    primitive_union: PrimitiveUnion | None


@dc.dataclass(frozen=True)
class RuntimeTypeKeys:
    nominal: TypeKey
    structural: TypeKey
    effective: TypeKey
    alpha_structural: TypeKey


@dc.dataclass(frozen=True)
class RuntimeCollectionShape:
    type_shape: RuntimeTypeShape
    iterable_item: Type | None
    sequence_item: Type | None
    set_item: Type | None
    mapping: tuple[Type, Type] | None


@dc.dataclass(frozen=True)
class RuntimeMappingShape:
    key: RuntimeTypeShape
    value: RuntimeTypeShape


@dc.dataclass(frozen=True)
class RuntimeDispatch:
    type_shape: RuntimeTypeShape
    collection_shape: RuntimeCollectionShape
    runtime_class: type | None
    is_any: bool
    is_none: bool


##


def _get_reflector(reflector: RuntimeTypeReflector | None) -> RuntimeTypeReflector:
    return DEFAULT_REFLECTOR if reflector is None else reflector


def _get_universe(universe: RuntimeTypeUniverse | None) -> RuntimeTypeUniverse:
    return DEFAULT_UNIVERSE if universe is None else universe


def get_runtime_class(
        typ: Type,
        universe: RuntimeTypeUniverse | None = None,
) -> type | None:
    if not isinstance(typ, Instance):
        return None
    return _get_universe(universe).get_runtime_type(typ._type)  # type: ignore[return-value]


def require_runtime_class(
        typ: Type,
        universe: RuntimeTypeUniverse | None = None,
) -> type:
    cls = get_runtime_class(typ, universe)
    if cls is None:
        raise ReflectionTypeError(f'Runtime class is unavailable for type: {typ!r}')
    return cls


def _is_new_type(obj: object) -> bool:
    return isinstance(obj, ta.NewType)


def get_runtime_new_type(
        typ: Type,
        universe: RuntimeTypeUniverse | None = None,
) -> object | None:
    if not isinstance(typ, Instance):
        return None

    obj = _get_universe(universe).get_runtime_type(typ._type)
    if obj is None or not _is_new_type(obj):
        return None
    return obj


def get_runtime_new_type_info(
        typ: Type,
        reflector: RuntimeTypeReflector | None = None,
) -> RuntimeNewType | None:
    rt_reflector = _get_reflector(reflector)
    obj = get_runtime_new_type(typ, rt_reflector.universe)
    if obj is None:
        return None

    runtime_supertype = obj.__supertype__  # type: ignore[attr-defined]
    return RuntimeNewType(
        obj,
        runtime_supertype,
        rt_reflector.reflect_type(runtime_supertype),
    )


def require_runtime_new_type_info(
        typ: Type,
        reflector: RuntimeTypeReflector | None = None,
) -> RuntimeNewType:
    info = get_runtime_new_type_info(typ, reflector)
    if info is None:
        raise ReflectionTypeError(f'Runtime NewType is unavailable for type: {typ!r}')
    return info


def get_runtime_new_type_supertype(
        typ: Type,
        reflector: RuntimeTypeReflector | None = None,
) -> Type | None:
    info = get_runtime_new_type_info(typ, reflector)
    if info is None:
        return None
    return info.supertype


def get_annotated(typ: Type) -> RuntimeAnnotated | None:
    if not isinstance(typ, AnnotatedType):
        return None

    metadata: list[object] = []
    item: Type = typ
    while isinstance(item, AnnotatedType):
        metadata.extend(item._metadata)
        item = item._item

    return RuntimeAnnotated(item, tuple(metadata))


def strip_annotated(typ: Type) -> Type:
    annotated = get_annotated(typ)
    if annotated is None:
        return typ
    return annotated.item


def get_runtime_type_alias(typ: Type) -> RuntimeTypeAlias | None:
    if not isinstance(typ, TypeAliasType):
        return None
    if typ._alias is None:
        raise ReflectionTypeError(f'Runtime type alias is unresolved: {typ!r}')
    return RuntimeTypeAlias(
        typ._alias._runtime_object,
        typ,
        get_type_alias_target(typ),
    )


def strip_runtime_type_alias(typ: Type) -> Type:
    alias = get_runtime_type_alias(typ)
    if alias is None:
        return typ
    return alias.target


def get_runtime_type_shape(
        typ: Type,
        reflector: RuntimeTypeReflector | None = None,
) -> RuntimeTypeShape:
    rt_reflector = _get_reflector(reflector)
    annotated = get_annotated(typ)
    unannotated = typ if annotated is None else annotated.item
    alias = get_runtime_type_alias(unannotated)
    unaliased = unannotated if alias is None else alias.target
    new_type = get_runtime_new_type_info(unaliased, rt_reflector)
    effective = unaliased if new_type is None else new_type.supertype
    return RuntimeTypeShape(
        typ,
        annotated,
        unannotated,
        alias,
        unaliased,
        new_type,
        effective,
        get_optional_item(effective),
        get_literal_value_type(effective),
        destructure_literal_union(effective),
        destructure_primitive_union(effective, universe=rt_reflector.universe),
    )


def get_runtime_unaliased_type_key(
        typ: Type,
        reflector: RuntimeTypeReflector | None = None,
) -> TypeKey:
    rt_reflector = _get_reflector(reflector)
    return rt_reflector.type_key(get_runtime_type_shape(typ, rt_reflector).unaliased)


def get_runtime_effective_type_key(
        typ: Type,
        reflector: RuntimeTypeReflector | None = None,
) -> TypeKey:
    # Historical compatibility name. This intentionally keys the unaliased view, preserving NewType identity.
    return get_runtime_unaliased_type_key(typ, reflector)


def get_runtime_type_keys(
        typ: Type,
        reflector: RuntimeTypeReflector | None = None,
) -> RuntimeTypeKeys:
    rt_reflector = _get_reflector(reflector)
    shape = get_runtime_type_shape(typ, rt_reflector)
    return RuntimeTypeKeys(
        rt_reflector.type_key(typ),
        rt_reflector.structural_type_key(typ),
        rt_reflector.type_key(shape.effective),
        rt_reflector.alpha_structural_type_key(typ),
    )


def get_instance_base_args(
        typ: Type,
        base: object,
        reflector: RuntimeTypeReflector | None = None,
) -> list[Type] | None:
    if not isinstance(typ, Instance):
        return None

    rt_reflector = _get_reflector(reflector)
    base_type = rt_reflector.reflect_type(base)
    if not isinstance(base_type, Instance):
        raise ReflectionTypeError(f'Unsupported base target: {base_type!r}')

    return get_base_args(typ, base_type._type)


def is_instance_of_runtime_base(
        typ: Type,
        base: object,
        reflector: RuntimeTypeReflector | None = None,
) -> bool:
    return get_instance_base_args(typ, base, reflector) is not None


def get_single_base_arg(
        typ: Type,
        base: object,
        reflector: RuntimeTypeReflector | None = None,
) -> Type | None:
    args = get_instance_base_args(typ, base, reflector)
    if args is None:
        return None
    if len(args) != 1:
        raise ReflectionTypeError(f'Expected one base argument for {typ!r} <: {base!r}, got {len(args)}')
    return args[0]


def get_mapping_base_args(
        typ: Type,
        base: object,
        reflector: RuntimeTypeReflector | None = None,
) -> tuple[Type, Type] | None:
    args = get_instance_base_args(typ, base, reflector)
    if args is None:
        return None
    if len(args) != 2:
        raise ReflectionTypeError(f'Expected two mapping base arguments for {typ!r} <: {base!r}, got {len(args)}')
    return args[0], args[1]


def get_effective_instance_base_args(
        typ: Type,
        base: object,
        reflector: RuntimeTypeReflector | None = None,
) -> list[Type] | None:
    rt_reflector = _get_reflector(reflector)
    return get_instance_base_args(get_runtime_type_shape(typ, rt_reflector).effective, base, rt_reflector)


def get_effective_single_base_arg(
        typ: Type,
        base: object,
        reflector: RuntimeTypeReflector | None = None,
) -> Type | None:
    rt_reflector = _get_reflector(reflector)
    return get_single_base_arg(get_runtime_type_shape(typ, rt_reflector).effective, base, rt_reflector)


def get_effective_mapping_base_args(
        typ: Type,
        base: object,
        reflector: RuntimeTypeReflector | None = None,
) -> tuple[Type, Type] | None:
    rt_reflector = _get_reflector(reflector)
    return get_mapping_base_args(get_runtime_type_shape(typ, rt_reflector).effective, base, rt_reflector)


def get_runtime_collection_shape(
        typ: Type,
        reflector: RuntimeTypeReflector | None = None,
) -> RuntimeCollectionShape:
    rt_reflector = _get_reflector(reflector)
    type_shape = get_runtime_type_shape(typ, rt_reflector)
    effective = type_shape.effective
    return RuntimeCollectionShape(
        type_shape,
        get_single_base_arg(effective, cabc.Iterable, rt_reflector),
        get_single_base_arg(effective, cabc.Sequence, rt_reflector),
        get_single_base_arg(effective, cabc.Set, rt_reflector),
        get_mapping_base_args(effective, cabc.Mapping, rt_reflector),
    )


def get_runtime_mapping_shape(
        typ: Type,
        reflector: RuntimeTypeReflector | None = None,
) -> RuntimeMappingShape | None:
    rt_reflector = _get_reflector(reflector)
    collection_shape = get_runtime_collection_shape(typ, rt_reflector)
    if collection_shape.mapping is None:
        return None

    key, value = collection_shape.mapping
    return RuntimeMappingShape(
        get_runtime_type_shape(key, rt_reflector),
        get_runtime_type_shape(value, rt_reflector),
    )


def get_runtime_dispatch(
        typ: Type,
        reflector: RuntimeTypeReflector | None = None,
) -> RuntimeDispatch:
    rt_reflector = _get_reflector(reflector)
    collection_shape = get_runtime_collection_shape(typ, rt_reflector)
    type_shape = collection_shape.type_shape
    effective = type_shape.effective
    return RuntimeDispatch(
        type_shape,
        collection_shape,
        get_runtime_class(effective, rt_reflector.universe),
        isinstance(effective, AnyType),
        isinstance(effective, NoneType),
    )


def is_optional_type(typ: Type) -> bool:
    return get_optional_item(typ) is not None


def get_optional_item(typ: Type) -> Type | None:
    if not isinstance(typ, UnionType):
        return None

    non_none: list[Type] = []
    seen_none = False
    for item in typ._items:
        if isinstance(item, NoneType):
            seen_none = True
        else:
            non_none.append(item)

    if not seen_none or len(non_none) != 1:
        return None

    return non_none[0]


def get_literal_value_type(typ: Type) -> LiteralValueType | None:
    values: list[LiteralValue] = []

    if isinstance(typ, LiteralType):
        values.append(typ._value)
    elif isinstance(typ, UnionType):
        for item in typ._items:
            if not isinstance(item, LiteralType):
                return None
            values.append(item._value)
    else:
        return None

    value_types = {type(value) for value in values}
    if len(value_types) != 1:
        return None

    return LiteralValueType(next(iter(value_types)), tuple(values))


def _get_runtime_literal_value(typ: LiteralType, universe: RuntimeTypeUniverse) -> object | None:
    cls = universe.get_runtime_type(typ._fallback._type)
    if (
            isinstance(cls, type)
            and issubclass(cls, enum.Enum)
            and isinstance(typ._value, str)
    ):
        try:
            return cls[typ._value]
        except KeyError:
            return None

    return typ._value


def get_runtime_literal_value_type(
        typ: Type,
        universe: RuntimeTypeUniverse | None = None,
) -> RuntimeLiteralValueType | None:
    rt_universe = _get_universe(universe)
    values: list[object] = []

    if isinstance(typ, LiteralType):
        value = _get_runtime_literal_value(typ, rt_universe)
        if value is None:
            return None
        values.append(value)
    elif isinstance(typ, UnionType):
        for item in typ._items:
            if not isinstance(item, LiteralType):
                return None
            value = _get_runtime_literal_value(item, rt_universe)
            if value is None:
                return None
            values.append(value)
    else:
        return None

    value_types = {type(value) for value in values}
    if len(value_types) != 1:
        return None

    return RuntimeLiteralValueType(next(iter(value_types)), tuple(values))


def destructure_literal_union(typ: Type) -> LiteralUnion | None:
    if not isinstance(typ, UnionType):
        return None

    literal_items: list[LiteralType] = []
    non_literals: list[Type] = []
    for item in typ._items:
        if isinstance(item, LiteralType):
            literal_items.append(item)
        else:
            non_literals.append(item)

    if not literal_items or len(non_literals) != 1:
        return None

    literal = UnionType(list(literal_items)) if len(literal_items) > 1 else literal_items[0]
    literal_info = get_literal_value_type(literal)
    if literal_info is None:
        return None

    return LiteralUnion(
        literal_info.value_type,
        literal,
        non_literals[0],
        literal_info.values,
    )


def destructure_primitive_union(
        typ: Type,
        primitives: ta.Container[type] = (float, int, str, bool),
        universe: RuntimeTypeUniverse | None = None,
) -> PrimitiveUnion | None:
    if not isinstance(typ, UnionType):
        return None

    rt_universe = _get_universe(universe)
    primitive_items: list[type] = []
    non_primitive_items: list[Type] = []
    for item in typ._items:
        cls = get_runtime_class(item, rt_universe)
        if cls is not None and cls in primitives:
            primitive_items.append(cls)
        else:
            non_primitive_items.append(item)

    if not primitive_items or len(non_primitive_items) > 1:
        return None

    return PrimitiveUnion(tuple(primitive_items), tuple(non_primitive_items))


def reflect_optional_item(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> Type | None:
    rt_reflector = _get_reflector(reflector)
    return get_optional_item(rt_reflector.reflect_type(obj))


def reflect_is_instance_of_runtime_base(
        obj: object,
        base: object,
        reflector: RuntimeTypeReflector | None = None,
) -> bool:
    rt_reflector = _get_reflector(reflector)
    return is_instance_of_runtime_base(rt_reflector.reflect_type(obj), base, rt_reflector)


def reflect_single_base_arg(
        obj: object,
        base: object,
        reflector: RuntimeTypeReflector | None = None,
) -> Type | None:
    rt_reflector = _get_reflector(reflector)
    return get_single_base_arg(rt_reflector.reflect_type(obj), base, rt_reflector)


def reflect_mapping_base_args(
        obj: object,
        base: object,
        reflector: RuntimeTypeReflector | None = None,
) -> tuple[Type, Type] | None:
    rt_reflector = _get_reflector(reflector)
    return get_mapping_base_args(rt_reflector.reflect_type(obj), base, rt_reflector)


def reflect_effective_instance_base_args(
        obj: object,
        base: object,
        reflector: RuntimeTypeReflector | None = None,
) -> list[Type] | None:
    rt_reflector = _get_reflector(reflector)
    return get_effective_instance_base_args(rt_reflector.reflect_type(obj), base, rt_reflector)


def reflect_effective_single_base_arg(
        obj: object,
        base: object,
        reflector: RuntimeTypeReflector | None = None,
) -> Type | None:
    rt_reflector = _get_reflector(reflector)
    return get_effective_single_base_arg(rt_reflector.reflect_type(obj), base, rt_reflector)


def reflect_effective_mapping_base_args(
        obj: object,
        base: object,
        reflector: RuntimeTypeReflector | None = None,
) -> tuple[Type, Type] | None:
    rt_reflector = _get_reflector(reflector)
    return get_effective_mapping_base_args(rt_reflector.reflect_type(obj), base, rt_reflector)


def reflect_runtime_new_type_info(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> RuntimeNewType | None:
    rt_reflector = _get_reflector(reflector)
    return get_runtime_new_type_info(rt_reflector.reflect_type(obj), rt_reflector)


def reflect_runtime_new_type_supertype(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> Type | None:
    rt_reflector = _get_reflector(reflector)
    return get_runtime_new_type_supertype(rt_reflector.reflect_type(obj), rt_reflector)


def reflect_annotated(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> RuntimeAnnotated | None:
    rt_reflector = _get_reflector(reflector)
    return get_annotated(rt_reflector.reflect_type(obj))


def reflect_strip_annotated(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> Type:
    rt_reflector = _get_reflector(reflector)
    return strip_annotated(rt_reflector.reflect_type(obj))


def reflect_runtime_type_alias(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> RuntimeTypeAlias | None:
    rt_reflector = _get_reflector(reflector)
    return get_runtime_type_alias(rt_reflector.reflect_type(obj))


def reflect_strip_runtime_type_alias(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> Type:
    rt_reflector = _get_reflector(reflector)
    return strip_runtime_type_alias(rt_reflector.reflect_type(obj))


def reflect_runtime_unaliased_type_key(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> TypeKey:
    rt_reflector = _get_reflector(reflector)
    return get_runtime_unaliased_type_key(rt_reflector.reflect_type(obj), rt_reflector)


def reflect_runtime_effective_type_key(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> TypeKey:
    # Historical compatibility name. This intentionally keys the unaliased view, preserving NewType identity.
    return reflect_runtime_unaliased_type_key(obj, reflector)


def reflect_runtime_type_keys(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> RuntimeTypeKeys:
    rt_reflector = _get_reflector(reflector)
    return get_runtime_type_keys(rt_reflector.reflect_type(obj), rt_reflector)


def reflect_runtime_type_shape(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> RuntimeTypeShape:
    rt_reflector = _get_reflector(reflector)
    return get_runtime_type_shape(rt_reflector.reflect_type(obj), rt_reflector)


def reflect_runtime_collection_shape(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> RuntimeCollectionShape:
    rt_reflector = _get_reflector(reflector)
    return get_runtime_collection_shape(rt_reflector.reflect_type(obj), rt_reflector)


def reflect_runtime_mapping_shape(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> RuntimeMappingShape | None:
    rt_reflector = _get_reflector(reflector)
    return get_runtime_mapping_shape(rt_reflector.reflect_type(obj), rt_reflector)


def reflect_runtime_dispatch(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> RuntimeDispatch:
    rt_reflector = _get_reflector(reflector)
    return get_runtime_dispatch(rt_reflector.reflect_type(obj), rt_reflector)


def reflect_literal_value_type(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> LiteralValueType | None:
    rt_reflector = _get_reflector(reflector)
    return get_literal_value_type(rt_reflector.reflect_type(obj))


def reflect_runtime_literal_value_type(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> RuntimeLiteralValueType | None:
    rt_reflector = _get_reflector(reflector)
    return get_runtime_literal_value_type(rt_reflector.reflect_type(obj), rt_reflector.universe)


def reflect_literal_union(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> LiteralUnion | None:
    rt_reflector = _get_reflector(reflector)
    return destructure_literal_union(rt_reflector.reflect_type(obj))


def reflect_primitive_union(
        obj: object,
        primitives: ta.Container[type] = (float, int, str, bool),
        reflector: RuntimeTypeReflector | None = None,
) -> PrimitiveUnion | None:
    rt_reflector = _get_reflector(reflector)
    return destructure_primitive_union(rt_reflector.reflect_type(obj), primitives, rt_reflector.universe)
