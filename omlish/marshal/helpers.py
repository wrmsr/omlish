import typing as ta

from .. import dataclasses as dc
from .objects import FieldMetadata


T = ta.TypeVar('T')


def update_fields_metadata(
        fields: ta.Iterable[str] | None = None,
        **kwargs: ta.Any,
) -> ta.Callable[[type[T]], type[T]]:
    def inner(a: str, f: dc.Field) -> dc.Field:
        return dc.update_field_metadata(f, {
            FieldMetadata: dc.replace(
                f.metadata.get(FieldMetadata, FieldMetadata()),
                **kwargs,
            ),
        })

    return dc.update_fields(inner, fields)
