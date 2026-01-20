"""
TODO:
 - @lang.copy_type
"""
import typing as ta

from ... import dataclasses as dc
from .types import DEFAULT_FIELD_OPTIONS
from .types import FieldOptions
from .types import ObjectOptions


T = ta.TypeVar('T')


##


def with_field_options(**kwargs: ta.Any) -> dc.field_modifier:
    @dc.field_modifier
    def inner(f: dc.Field) -> dc.Field:
        existing = f.metadata.get(FieldOptions, DEFAULT_FIELD_OPTIONS)
        updated = dc.replace(existing, **kwargs)
        return dc.set_field_metadata(f, {FieldOptions: updated})

    return inner


def update_fields_options(
        fields: ta.Iterable[str] | None = None,
        **kwargs: ta.Any,
) -> ta.Callable[[type[T]], type[T]]:
    def inner(a: str, f: dc.Field) -> dc.Field:
        existing = f.metadata.get(FieldOptions, DEFAULT_FIELD_OPTIONS)
        updated = dc.replace(existing, **kwargs)
        return dc.set_field_metadata(f, {FieldOptions: updated})

    return dc.update_fields(inner, fields)


def update_object_options(
        cls: type | None = None,
        **kwargs: ta.Any,
):
    def inner(cls):
        return dc.append_class_metadata(cls, ObjectOptions(**kwargs))

    if cls is not None:
        inner(cls)
        return cls
    else:
        return inner
