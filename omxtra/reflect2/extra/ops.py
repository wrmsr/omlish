# ruff: noqa: SLF001
import typing as ta

from ..core.compat import is_assignable
from ..core.compat import is_assignable_or_false
from ..core.join import join_type_list
from ..core.join import join_types
from ..core.join import structural_join_type_list
from ..core.join import structural_join_types
from ..core.meet import meet_type_list
from ..core.meet import meet_types
from ..core.meet import structural_meet_type_list
from ..core.meet import structural_meet_types
from ..core.strconv import type_str
from ..core.substitute import SubstitutionKey
from ..core.substitute import substitute_type
from ..core.substitute import substitute_types
from ..core.subtypes import MroEntry
from ..core.subtypes import get_base_args
from ..core.subtypes import get_base_args_or_none
from ..core.subtypes import get_base_instance
from ..core.subtypes import get_base_instance_or_none
from ..core.subtypes import get_mro_entries
from ..core.subtypes import get_mro_entries_or_none
from ..core.subtypes import get_mro_instances
from ..core.subtypes import get_mro_instances_or_none
from ..core.subtypes import is_alpha_equivalent
from ..core.subtypes import is_alpha_structurally_equivalent
from ..core.subtypes import is_same_type
from ..core.subtypes import is_structural_subtype
from ..core.subtypes import is_structurally_equivalent
from ..core.symbols import TypeInfo
from ..core.typekeys import TypeKey
from ..core.typeops import get_literal_values
from ..core.typeops import get_literal_values_or_none
from ..core.types import Instance
from ..core.types import LiteralValue
from ..core.types import Type
from ..core.types import TypedDictType
from ..core.types import TypeVarId
from ..core.types import TypeVarLikeType
from ..errors import ReflectionTypeError
from ..errors import UnsupportedTypeOperationError
from ..reflect import DEFAULT_REFLECTOR
from ..reflect import TypeReflector


RuntimeSubstitutionMap: ta.TypeAlias = ta.Mapping[object, object]


##


def reflect_join(
        left: object,
        right: object,
        reflector: TypeReflector | None = None,
) -> Type:
    rt_reflector = _get_reflector(reflector)
    return join_types(rt_reflector.reflect_type(left), rt_reflector.reflect_type(right))


def reflect_join_list(
        items: list[object],
        reflector: TypeReflector | None = None,
) -> Type:
    rt_reflector = _get_reflector(reflector)
    return join_type_list([rt_reflector.reflect_type(item) for item in items])


def reflect_structural_join(
        left: object,
        right: object,
        reflector: TypeReflector | None = None,
) -> Type:
    rt_reflector = _get_reflector(reflector)
    return structural_join_types(rt_reflector.reflect_type(left), rt_reflector.reflect_type(right))


def reflect_structural_join_list(
        items: list[object],
        reflector: TypeReflector | None = None,
) -> Type:
    rt_reflector = _get_reflector(reflector)
    return structural_join_type_list([rt_reflector.reflect_type(item) for item in items])


def reflect_meet(
        left: object,
        right: object,
        reflector: TypeReflector | None = None,
) -> Type:
    rt_reflector = _get_reflector(reflector)
    return meet_types(rt_reflector.reflect_type(left), rt_reflector.reflect_type(right))


def reflect_meet_list(
        items: list[object],
        reflector: TypeReflector | None = None,
) -> Type:
    rt_reflector = _get_reflector(reflector)
    return meet_type_list([rt_reflector.reflect_type(item) for item in items])


def reflect_structural_meet(
        left: object,
        right: object,
        reflector: TypeReflector | None = None,
) -> Type:
    rt_reflector = _get_reflector(reflector)
    return structural_meet_types(rt_reflector.reflect_type(left), rt_reflector.reflect_type(right))


def reflect_structural_meet_list(
        items: list[object],
        reflector: TypeReflector | None = None,
) -> Type:
    rt_reflector = _get_reflector(reflector)
    return structural_meet_type_list([rt_reflector.reflect_type(item) for item in items])


def reflect_is_assignable(
        source: object,
        target: object,
        reflector: TypeReflector | None = None,
) -> bool:
    rt_reflector = _get_reflector(reflector)
    return is_assignable(rt_reflector.reflect_type(source), rt_reflector.reflect_type(target))


def reflect_is_assignable_or_false(
        source: object,
        target: object,
        reflector: TypeReflector | None = None,
) -> bool:
    rt_reflector = _get_reflector(reflector)
    return is_assignable_or_false(rt_reflector.reflect_type(source), rt_reflector.reflect_type(target))


def reflect_is_structural_subtype(
        source: object,
        target: object,
        reflector: TypeReflector | None = None,
) -> bool:
    rt_reflector = _get_reflector(reflector)
    return is_structural_subtype(rt_reflector.reflect_type(source), rt_reflector.reflect_type(target))


def reflect_is_structural_subtype_or_false(
        source: object,
        target: object,
        reflector: TypeReflector | None = None,
) -> bool:
    try:
        return reflect_is_structural_subtype(source, target, reflector)
    except UnsupportedTypeOperationError:
        return False


def reflect_is_same_type(
        left: object,
        right: object,
        reflector: TypeReflector | None = None,
) -> bool:
    rt_reflector = _get_reflector(reflector)
    return is_same_type(rt_reflector.reflect_type(left), rt_reflector.reflect_type(right))


def reflect_is_alpha_equivalent(
        left: object,
        right: object,
        reflector: TypeReflector | None = None,
) -> bool:
    rt_reflector = _get_reflector(reflector)
    return is_alpha_equivalent(rt_reflector.reflect_type(left), rt_reflector.reflect_type(right))


def reflect_is_structurally_equivalent(
        left: object,
        right: object,
        reflector: TypeReflector | None = None,
) -> bool:
    rt_reflector = _get_reflector(reflector)
    return is_structurally_equivalent(rt_reflector.reflect_type(left), rt_reflector.reflect_type(right))


def reflect_is_structurally_equivalent_or_false(
        left: object,
        right: object,
        reflector: TypeReflector | None = None,
) -> bool:
    try:
        return reflect_is_structurally_equivalent(left, right, reflector)
    except UnsupportedTypeOperationError:
        return False


def reflect_is_alpha_structurally_equivalent(
        left: object,
        right: object,
        reflector: TypeReflector | None = None,
) -> bool:
    rt_reflector = _get_reflector(reflector)
    return is_alpha_structurally_equivalent(rt_reflector.reflect_type(left), rt_reflector.reflect_type(right))


def reflect_is_alpha_structurally_equivalent_or_false(
        left: object,
        right: object,
        reflector: TypeReflector | None = None,
) -> bool:
    try:
        return reflect_is_alpha_structurally_equivalent(left, right, reflector)
    except UnsupportedTypeOperationError:
        return False


def reflect_type_str(
        obj: object,
        reflector: TypeReflector | None = None,
) -> str:
    rt_reflector = _get_reflector(reflector)
    return type_str(rt_reflector.reflect_type(obj))


def reflect_type_strs(
        objs: list[object],
        reflector: TypeReflector | None = None,
) -> ta.Sequence[str]:
    rt_reflector = _get_reflector(reflector)
    return [
        type_str(rt_reflector.reflect_type(obj))
        for obj in objs
    ]


def reflect_type_key(
        obj: object,
        reflector: TypeReflector | None = None,
) -> TypeKey:
    rt_reflector = _get_reflector(reflector)
    return rt_reflector.type_key(rt_reflector.reflect_type(obj))


def reflect_type_key_or_none(
        obj: object,
        reflector: TypeReflector | None = None,
) -> TypeKey | None:
    rt_reflector = _get_reflector(reflector)
    return rt_reflector.type_key_or_none(rt_reflector.reflect_type(obj))


def reflect_alpha_type_key(
        obj: object,
        reflector: TypeReflector | None = None,
) -> TypeKey:
    rt_reflector = _get_reflector(reflector)
    return rt_reflector.alpha_type_key(rt_reflector.reflect_type(obj))


def reflect_alpha_type_key_or_none(
        obj: object,
        reflector: TypeReflector | None = None,
) -> TypeKey | None:
    rt_reflector = _get_reflector(reflector)
    return rt_reflector.alpha_type_key_or_none(rt_reflector.reflect_type(obj))


def reflect_structural_type_key(
        obj: object,
        reflector: TypeReflector | None = None,
) -> TypeKey:
    rt_reflector = _get_reflector(reflector)
    return rt_reflector.structural_type_key(rt_reflector.reflect_type(obj))


def reflect_structural_type_key_or_none(
        obj: object,
        reflector: TypeReflector | None = None,
) -> TypeKey | None:
    rt_reflector = _get_reflector(reflector)
    return rt_reflector.structural_type_key_or_none(rt_reflector.reflect_type(obj))


def reflect_alpha_structural_type_key(
        obj: object,
        reflector: TypeReflector | None = None,
) -> TypeKey:
    rt_reflector = _get_reflector(reflector)
    return rt_reflector.alpha_structural_type_key(rt_reflector.reflect_type(obj))


def reflect_alpha_structural_type_key_or_none(
        obj: object,
        reflector: TypeReflector | None = None,
) -> TypeKey | None:
    rt_reflector = _get_reflector(reflector)
    return rt_reflector.alpha_structural_type_key_or_none(rt_reflector.reflect_type(obj))


def reflect_literal_values(
        obj: object,
        reflector: TypeReflector | None = None,
) -> ta.Sequence[LiteralValue]:
    rt_reflector = _get_reflector(reflector)
    return get_literal_values(rt_reflector.reflect_type(obj))


def reflect_literal_values_or_none(
        obj: object,
        reflector: TypeReflector | None = None,
) -> ta.Sequence[LiteralValue] | None:
    rt_reflector = _get_reflector(reflector)
    return get_literal_values_or_none(rt_reflector.reflect_type(obj))


def reflect_typed_dict_literal_values(
        obj: object,
        reflector: TypeReflector | None = None,
) -> ta.Mapping[str, list[LiteralValue] | None]:
    typ = _get_reflector(reflector).reflect_type(obj)
    if not isinstance(typ, TypedDictType):
        raise ReflectionTypeError(f'Unsupported TypedDict type: {typ!r}')
    return {
        name: get_literal_values_or_none(item)
        for name, item in typ._items.items()
    }


def reflect_instance(
        obj: object,
        reflector: TypeReflector | None = None,
) -> Instance:
    typ = _get_reflector(reflector).reflect_type(obj)
    if not isinstance(typ, Instance):
        raise ReflectionTypeError(f'Unsupported instance type: {typ!r}')
    return typ


def reflect_instance_info(
        obj: object,
        reflector: TypeReflector | None = None,
) -> TypeInfo:
    return reflect_instance(obj, reflector)._type


def reflect_instance_args(
        obj: object,
        reflector: TypeReflector | None = None,
) -> ta.Sequence[Type]:
    return reflect_instance(obj, reflector)._args


def reflect_base_args(
        source: object,
        target: object,
        reflector: TypeReflector | None = None,
) -> ta.Sequence[Type] | None:
    rt_reflector = _get_reflector(reflector)
    return _reflect_base_args(source, target, rt_reflector)


def reflect_base_args_or_none(
        source: object,
        target: object,
        reflector: TypeReflector | None = None,
) -> ta.Sequence[Type] | None:
    rt_reflector = _get_reflector(reflector)
    return _reflect_base_args(source, target, rt_reflector, strict=False)


def reflect_base_instance(
        source: object,
        target: object,
        reflector: TypeReflector | None = None,
) -> Instance | None:
    rt_reflector = _get_reflector(reflector)
    source_type, target_type = _reflect_base_instance_inputs(source, target, rt_reflector)
    return get_base_instance(source_type, target_type._type)


def reflect_base_instance_or_none(
        source: object,
        target: object,
        reflector: TypeReflector | None = None,
) -> Instance | None:
    rt_reflector = _get_reflector(reflector)
    source_type, target_type = _reflect_base_instance_inputs(source, target, rt_reflector)
    return get_base_instance_or_none(source_type, target_type._type)


def reflect_mro_instances(
        source: object,
        reflector: TypeReflector | None = None,
) -> ta.Sequence[Instance]:
    rt_reflector = _get_reflector(reflector)
    source_type = rt_reflector.reflect_type(source)
    if not isinstance(source_type, Instance):
        raise ReflectionTypeError(f'Unsupported MRO source: {source_type!r}')
    return get_mro_instances(source_type)


def reflect_mro_instances_or_none(
        source: object,
        reflector: TypeReflector | None = None,
) -> ta.Sequence[Instance] | None:
    rt_reflector = _get_reflector(reflector)
    source_type = rt_reflector.reflect_type(source)
    if not isinstance(source_type, Instance):
        raise ReflectionTypeError(f'Unsupported MRO source: {source_type!r}')
    return get_mro_instances_or_none(source_type)


def reflect_mro_entries(
        source: object,
        reflector: TypeReflector | None = None,
) -> ta.Sequence[MroEntry]:
    rt_reflector = _get_reflector(reflector)
    source_type = rt_reflector.reflect_type(source)
    if not isinstance(source_type, Instance):
        raise ReflectionTypeError(f'Unsupported MRO source: {source_type!r}')
    return get_mro_entries(source_type)


def reflect_mro_entries_or_none(
        source: object,
        reflector: TypeReflector | None = None,
) -> ta.Sequence[MroEntry] | None:
    rt_reflector = _get_reflector(reflector)
    source_type = rt_reflector.reflect_type(source)
    if not isinstance(source_type, Instance):
        raise ReflectionTypeError(f'Unsupported MRO source: {source_type!r}')
    return get_mro_entries_or_none(source_type)


def reflect_mro_type_strs(
        source: object,
        reflector: TypeReflector | None = None,
) -> ta.Sequence[str]:
    return [
        type_str(instance)
        for instance in reflect_mro_instances(source, reflector)
    ]


def _reflect_base_args(
        source: object,
        target: object,
        rt_reflector: TypeReflector,
        *,
        strict: bool = True,
) -> ta.Sequence[Type] | None:
    source_type, target_type = _reflect_base_instance_inputs(source, target, rt_reflector)

    if strict:
        return get_base_args(source_type, target_type._type)
    return get_base_args_or_none(source_type, target_type._type)


def _reflect_base_instance_inputs(
        source: object,
        target: object,
        rt_reflector: TypeReflector,
) -> tuple[Instance, Instance]:
    source_type = rt_reflector.reflect_type(source)
    target_type = rt_reflector.reflect_type(target)

    if not isinstance(source_type, Instance):
        raise ReflectionTypeError(f'Unsupported base source: {source_type!r}')
    if not isinstance(target_type, Instance):
        raise ReflectionTypeError(f'Unsupported base target: {target_type!r}')

    return source_type, target_type


def reflect_substitute_type(
        typ: object,
        replacements: RuntimeSubstitutionMap,
        reflector: TypeReflector | None = None,
) -> Type:
    rt_reflector = _get_reflector(reflector)
    reflected_type = rt_reflector.reflect_type(typ)
    return substitute_type(reflected_type, _reflect_replacements(replacements, rt_reflector))


def reflect_substitute_types(
        typs: list[object],
        replacements: RuntimeSubstitutionMap,
        reflector: TypeReflector | None = None,
) -> ta.Sequence[Type]:
    rt_reflector = _get_reflector(reflector)
    reflected_replacements = _reflect_replacements(replacements, rt_reflector)
    return substitute_types(
        [rt_reflector.reflect_type(typ) for typ in typs],
        reflected_replacements,
    )


def _get_reflector(reflector: TypeReflector | None) -> TypeReflector:
    if reflector is None:
        return DEFAULT_REFLECTOR
    return reflector


def _reflect_replacements(
        replacements: RuntimeSubstitutionMap,
        reflector: TypeReflector,
) -> ta.Mapping[SubstitutionKey, Type]:
    reflected: dict[SubstitutionKey, Type] = {}

    for key, value in replacements.items():
        if isinstance(key, (TypeVarId, TypeVarLikeType)):
            reflected_key = key
        else:
            key_type = reflector.reflect_type(key)
            if not isinstance(key_type, TypeVarLikeType):
                raise ReflectionTypeError(f'Unsupported runtime substitution key: {key!r}')
            reflected_key = key_type

        reflected[reflected_key] = reflector.reflect_type(value)

    return reflected
