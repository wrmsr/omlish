# ruff: noqa: SLF001
import dataclasses as dc
import typing as ta

from .core.substitute import substitute_type
from .core.subtypes import MroEntry
from .core.types import Type
from .errors import ReflectionTypeError
from .errors import UnsupportedTypeOperationError
from .globals import or_global_mirror
from .mirror import Mirror
from .ops import reflect_mro_entries_by_info


##


@dc.dataclass(frozen=True)
class DataclassField:
    field: dc.Field
    name: str
    owner: type
    raw_type: Type
    replaced_type: Type


@dc.dataclass(frozen=True)
class DataclassInspection:
    origin: type
    fields: tuple[DataclassField, ...]
    fields_by_name: ta.Mapping[str, DataclassField]


##


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


class DataclassInspector:
    def __init__(self, mirror: Mirror) -> None:
        super().__init__()

        self._mirror = mirror

    def inspect_dataclass(self, obj: object) -> DataclassInspection:
        origin = _get_origin_dataclass(obj)
        owners = _get_dataclass_field_owners(origin)
        entries_by_info = reflect_mro_entries_by_info(obj, mirror=self._mirror)

        ret: list[DataclassField] = []
        for field in dc.fields(origin):
            try:
                owner = owners[field.name]
            except KeyError:
                raise ReflectionTypeError(f'Missing dataclass field owner: {origin!r}.{field.name}') from None

            owner_info = self._mirror.get_type_info(owner)
            try:
                owner_entry = entries_by_info[owner_info]
            except KeyError:
                raise UnsupportedTypeOperationError(
                    f'Dataclass field owner is not in reflected MRO: {origin!r}.{field.name}',
                ) from None

            raw_type = self._mirror.reflect_type(_get_field_annotation(field, owner))
            ret.append(DataclassField(
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
        return DataclassInspection(
            origin,
            fields,
            fields_by_name,
        )


def inspect_dataclass(obj: object, *, mirror: Mirror | None = None) -> DataclassInspection:
    return DataclassInspector(or_global_mirror(mirror)).inspect_dataclass(obj)
