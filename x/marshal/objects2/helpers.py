import typing as ta

from omlish import dataclasses as dc

from .metadata import FieldMetadata
from .metadata import ObjectMetadata


T = ta.TypeVar('T')


##


def with_field_metadata(**kwargs: ta.Any) -> dc.field_modifier:
    """Create a field modifier that sets FieldMetadata on a dataclass field."""

    @dc.field_modifier
    def inner(f: dc.Field) -> dc.Field:
        # Get existing metadata or create new
        existing = f.metadata.get(FieldMetadata, FieldMetadata())

        # Merge with new kwargs - simply use dc.replace since we have a flat structure now
        updated = dc.replace(existing, **kwargs)

        return dc.set_field_metadata(f, {
            FieldMetadata: updated,
        })

    return inner


def update_fields_metadata(
        fields: ta.Iterable[str] | None = None,
        **kwargs: ta.Any,
) -> ta.Callable[[type[T]], type[T]]:
    """
    Class decorator to update FieldMetadata on specific fields.

    Args:
        fields: Field names to update. If None, updates all fields.
        **kwargs: FieldMetadata attributes to set.
    """

    def inner(a: str, f: dc.Field) -> dc.Field:
        existing = f.metadata.get(FieldMetadata, FieldMetadata())
        updated = dc.replace(existing, **kwargs)

        return dc.set_field_metadata(f, {
            FieldMetadata: updated,
        })

    return dc.update_fields(inner, fields)


def update_object_metadata(
        cls: type | None = None,
        **kwargs: ta.Any,
):
    """
    Class decorator to set ObjectMetadata.

    Can be used as @update_object_metadata(field_naming=...) or update_object_metadata(cls, ...).
    """

    def inner(cls):
        return dc.append_class_metadata(cls, ObjectMetadata(**kwargs))

    if cls is not None:
        inner(cls)
        return cls
    else:
        return inner
