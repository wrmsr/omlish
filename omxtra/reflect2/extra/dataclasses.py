# ruff: noqa: SLF001
import dataclasses as dc
import typing as ta

from ..core.substitute import substitute_type
from ..core.subtypes import MroEntry
from ..core.typekeys import TypeKey
from ..core.typekeys import type_key
from ..core.types import Type
from ..errors import ReflectionTypeError
from ..errors import UnsupportedTypeOperationError
from ..reflect import DEFAULT_REFLECTOR
from ..reflect import RuntimeTypeReflector
from .ops import reflect_mro_entries


##


@dc.dataclass(frozen=True)
class RuntimeDataclassField:
    field: dc.Field
    name: str
    owner: type
    raw_type: Type
    replaced_type: Type


@dc.dataclass(frozen=True)
class RuntimeDataclassInspection:
    origin: type
    fields: tuple[RuntimeDataclassField, ...]
    fields_by_name: dict[str, RuntimeDataclassField]
    field_types: dict[str, Type]
    field_type_keys: dict[str, TypeKey]
    field_structural_type_keys: dict[str, TypeKey]
    field_annotations: dict[str, object]


##


def _get_reflector(reflector: RuntimeTypeReflector | None) -> RuntimeTypeReflector:
    return DEFAULT_REFLECTOR if reflector is None else reflector


def _get_origin_dataclass(obj: object) -> type:
    origin = ta.get_origin(obj)
    if origin is None:
        origin = obj

    if not isinstance(origin, type) or not dc.is_dataclass(origin):
        raise ReflectionTypeError(f'Unsupported dataclass source: {obj!r}')

    return origin


def _get_dataclass_field_owners(origin: type) -> dict[str, type]:
    field_names = {field.name for field in dc.fields(origin)}
    owners: dict[str, type] = {}

    for cls in reversed(origin.__mro__):
        if not isinstance(cls, type) or not dc.is_dataclass(cls):
            continue

        annotations = getattr(cls, '__annotations__', {})
        if not isinstance(annotations, dict):
            raise ReflectionTypeError(f'Unsupported dataclass annotations for {cls!r}: {annotations!r}')

        class_fields = getattr(cls, '__dataclass_fields__', {})
        if not isinstance(class_fields, dict):
            raise ReflectionTypeError(f'Unsupported dataclass fields for {cls!r}: {class_fields!r}')

        for name in annotations:
            if name in field_names and name in class_fields:
                owners[name] = cls

    return owners


def _get_mro_entries_by_info(
        obj: object,
        reflector: RuntimeTypeReflector,
) -> dict[object, MroEntry]:
    return {
        entry._info: entry
        for entry in reflect_mro_entries(obj, reflector)
    }


def _get_field_annotation(field: dc.Field, owner: type) -> object:
    annotations = getattr(owner, '__annotations__', {})
    if not isinstance(annotations, dict):
        raise ReflectionTypeError(f'Unsupported dataclass annotations for {owner!r}: {annotations!r}')
    return annotations.get(field.name, field.type)


def _replace_field_type(
        raw_type: Type,
        owner_entry: MroEntry,
) -> Type:
    owner_type_vars = owner_entry._info._type_vars
    if not owner_type_vars:
        return raw_type

    if len(owner_type_vars) != len(owner_entry._args):
        raise UnsupportedTypeOperationError(
            f'Cannot replace dataclass field type with mismatched owner args: {owner_entry._instance!r}',
        )

    return substitute_type(raw_type, dict(zip(owner_type_vars, owner_entry._args)))


def inspect_dataclass(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> RuntimeDataclassInspection:
    rt_reflector = _get_reflector(reflector)
    return ta.cast(RuntimeDataclassInspection, rt_reflector.cached_inspection(
        'dataclass',
        obj,
        lambda: _inspect_dataclass_uncached(obj, rt_reflector),
    ))


def _inspect_dataclass_uncached(
        obj: object,
        rt_reflector: RuntimeTypeReflector,
) -> RuntimeDataclassInspection:
    origin = _get_origin_dataclass(obj)
    owners = _get_dataclass_field_owners(origin)
    entries_by_info = _get_mro_entries_by_info(obj, rt_reflector)

    ret: list[RuntimeDataclassField] = []
    for field in dc.fields(origin):
        try:
            owner = owners[field.name]
        except KeyError:
            raise ReflectionTypeError(f'Missing dataclass field owner: {origin!r}.{field.name}') from None

        owner_info = rt_reflector.universe.get_type_info(owner)
        try:
            owner_entry = entries_by_info[owner_info]
        except KeyError:
            raise UnsupportedTypeOperationError(
                f'Dataclass field owner is not in reflected MRO: {origin!r}.{field.name}',
            ) from None

        raw_type = rt_reflector.reflect_type(_get_field_annotation(field, owner))
        ret.append(RuntimeDataclassField(
            field,
            field.name,
            owner,
            raw_type,
            _replace_field_type(raw_type, owner_entry),
        ))

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
    return RuntimeDataclassInspection(
        origin,
        fields,
        fields_by_name,
        field_types,
        field_type_keys,
        field_structural_type_keys,
        field_annotations,
    )


def reflect_dataclass_fields(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> list[RuntimeDataclassField]:
    return list(inspect_dataclass(obj, reflector).fields)


def reflect_dataclass_field_types(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> dict[str, Type]:
    return dict(inspect_dataclass(obj, reflector).field_types)


def reflect_dataclass_field_type_keys(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> dict[str, TypeKey]:
    return dict(inspect_dataclass(obj, reflector).field_type_keys)


def reflect_dataclass_field_structural_type_keys(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> dict[str, TypeKey]:
    return dict(inspect_dataclass(obj, reflector).field_structural_type_keys)


def reflect_dataclass_field_annotations(
        obj: object,
        reflector: RuntimeTypeReflector | None = None,
) -> dict[str, object]:
    return dict(inspect_dataclass(obj, reflector).field_annotations)
