# ruff: noqa: SLF001
import dataclasses as dc
import typing as ta

from ..core.substitute import substitute_type
from ..core.typekeys import TypeKey
from ..core.typekeys import type_key
from ..core.types import Instance
from ..core.types import Type
from ..core.types import TypeVarLikeType
from ..errors import ReflectionTypeError
from ..errors import UnsupportedTypeOperationError
from ..reflect import DEFAULT_REFLECTOR
from ..reflect import TypeReflector


##


@dc.dataclass(frozen=True)
class RuntimeNamedTupleField:
    name: str
    raw_type: Type
    replaced_type: Type


@dc.dataclass(frozen=True)
class RuntimeNamedTupleInspection:
    origin: type
    fields: tuple[RuntimeNamedTupleField, ...]
    fields_by_name: dict[str, RuntimeNamedTupleField]
    field_types: dict[str, Type]
    field_type_keys: dict[str, TypeKey]
    field_structural_type_keys: dict[str, TypeKey]
    field_annotations: dict[str, object]


##


def _get_reflector(reflector: TypeReflector | None) -> TypeReflector:
    return DEFAULT_REFLECTOR if reflector is None else reflector


def _get_origin_namedtuple(obj: object) -> type:
    origin = ta.get_origin(obj)
    if origin is None:
        origin = obj

    if not isinstance(origin, type) or not is_namedtuple(origin):
        raise ReflectionTypeError(f'Unsupported namedtuple source: {obj!r}')

    return origin


def is_namedtuple(obj: object) -> bool:
    return (
        isinstance(obj, type)
        and issubclass(obj, tuple)
        and ta.NamedTuple in getattr(obj, '__orig_bases__', ())
        and isinstance(getattr(obj, '_fields', None), tuple)
    )


def _get_namedtuple_annotations(origin: type) -> dict[str, object]:
    annotations = getattr(origin, '__annotations__', {})
    if not isinstance(annotations, dict):
        raise ReflectionTypeError(f'Unsupported namedtuple annotations for {origin!r}: {annotations!r}')
    return annotations


def _get_replacements(
        obj: object,
        origin: type,
        reflector: TypeReflector,
) -> dict[TypeVarLikeType, Type]:
    instance = reflector.reflect_type(obj)
    if not isinstance(instance, Instance):
        raise ReflectionTypeError(f'Unsupported namedtuple reflected type: {instance!r}')

    origin_info = reflector.universe.get_type_info(origin)
    if instance._type is not origin_info:
        raise UnsupportedTypeOperationError(f'Namedtuple origin mismatch: {instance!r} != {origin_info._fullname}')

    if not origin_info._type_vars:
        return {}

    if len(origin_info.type_vars) != len(instance._args):
        raise UnsupportedTypeOperationError(f'Cannot replace namedtuple field type with mismatched args: {instance!r}')

    return dict(zip(origin_info.type_vars, instance._args))


def inspect_namedtuple(
        obj: object,
        reflector: TypeReflector | None = None,
) -> RuntimeNamedTupleInspection:
    rt_reflector = _get_reflector(reflector)
    return ta.cast(RuntimeNamedTupleInspection, rt_reflector.cached_inspection(
        'namedtuple',
        obj,
        lambda: _inspect_namedtuple_uncached(obj, rt_reflector),
    ))


def _inspect_namedtuple_uncached(
        obj: object,
        rt_reflector: TypeReflector,
) -> RuntimeNamedTupleInspection:
    origin = _get_origin_namedtuple(obj)
    annotations = _get_namedtuple_annotations(origin)
    replacements = _get_replacements(obj, origin, rt_reflector)

    ret: list[RuntimeNamedTupleField] = []
    for name in getattr(origin, '_fields'):
        try:
            annotation = annotations[name]
        except KeyError:
            raise ReflectionTypeError(f'Missing namedtuple field annotation: {origin!r}.{name}') from None

        raw_type = rt_reflector.reflect_type(annotation)
        replaced_type = (
            substitute_type(raw_type, replacements)
            if replacements else raw_type
        )
        ret.append(RuntimeNamedTupleField(name, raw_type, replaced_type))

    fields = tuple(ret)
    fields_by_name = {
        field.name: field
        for field in fields
    }
    field_types = {
        field.name: field.replaced_type
        for field in fields
    }
    field_type_keys = {
        field.name: type_key(field.replaced_type)
        for field in fields
    }
    field_structural_type_keys = {
        field.name: rt_reflector.structural_type_key(field.replaced_type)
        for field in fields
    }
    field_annotations = {
        field.name: rt_reflector.to_runtime_annotation(field.replaced_type)
        for field in fields
    }
    return RuntimeNamedTupleInspection(
        origin,
        fields,
        fields_by_name,
        field_types,
        field_type_keys,
        field_structural_type_keys,
        field_annotations,
    )


def reflect_namedtuple_fields(
        obj: object,
        reflector: TypeReflector | None = None,
) -> list[RuntimeNamedTupleField]:
    return list(inspect_namedtuple(obj, reflector).fields)


def reflect_namedtuple_field_types(
        obj: object,
        reflector: TypeReflector | None = None,
) -> dict[str, Type]:
    return dict(inspect_namedtuple(obj, reflector).field_types)


def reflect_namedtuple_field_type_keys(
        obj: object,
        reflector: TypeReflector | None = None,
) -> dict[str, TypeKey]:
    return dict(inspect_namedtuple(obj, reflector).field_type_keys)


def reflect_namedtuple_field_structural_type_keys(
        obj: object,
        reflector: TypeReflector | None = None,
) -> dict[str, TypeKey]:
    return dict(inspect_namedtuple(obj, reflector).field_structural_type_keys)


def reflect_namedtuple_field_annotations(
        obj: object,
        reflector: TypeReflector | None = None,
) -> dict[str, object]:
    return dict(inspect_namedtuple(obj, reflector).field_annotations)
