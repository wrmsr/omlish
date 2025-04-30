import typing as ta

from ... import dataclasses as dc
from .metadata import FieldMetadata
from .metadata import ObjectMetadata


T = ta.TypeVar('T')


##


def with_field_metadata(**kwargs: ta.Any) -> dc.field_modifier:
    @dc.field_modifier
    def inner(f: dc.Field) -> dc.Field:
        return dc.set_field_metadata(f, {
            FieldMetadata: f.metadata.get(FieldMetadata, FieldMetadata()).update(**kwargs),
        })
    return inner


def update_fields_metadata(
        fields: ta.Iterable[str] | None = None,
        **kwargs: ta.Any,
) -> ta.Callable[[type[T]], type[T]]:
    def inner(a: str, f: dc.Field) -> dc.Field:
        return dc.set_field_metadata(f, {
            FieldMetadata: f.metadata.get(FieldMetadata, FieldMetadata()).update(**kwargs),
        })

    return dc.update_fields(inner, fields)


def update_object_metadata(
        cls: type | None = None,
        **kwargs: ta.Any,
):
    def inner(cls):
        return dc.append_class_metadata(cls, ObjectMetadata(**kwargs))

    if cls is not None:
        inner(cls)
        return cls
    else:
        return inner
