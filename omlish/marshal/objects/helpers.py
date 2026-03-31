import typing as ta

from ... import dataclasses as dc
from ... import lang
from ..api.naming import Naming
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory
from .api import DEFAULT_FIELD_OPTIONS
from .api import FieldOptions
from .api import ObjectOptions


T = ta.TypeVar('T')


##
# The following functions duplicate kwargs/defaults from the api objects, but does so only for autocomplete - the
# underlying impl blindly forwards given kwargs to allow distinction between `None` and absent.


def _with_field_options(
        **kwargs: ta.Any,
) -> dc.field_modifier:
    @dc.field_modifier
    def inner(f: dc.Field) -> dc.Field:
        existing = f.metadata.get(FieldOptions, DEFAULT_FIELD_OPTIONS)
        updated = dc.replace(existing, **kwargs)
        return dc.set_field_metadata(f, {FieldOptions: updated})

    return inner


def with_field_options(
        name: str | None = None,
        alts: ta.Iterable[str] | None = None,

        omit_if: ta.Callable[[ta.Any], bool] | None = None,
        default: lang.Maybe[ta.Any] | None = None,
        embed: bool | None = None,
        generic_replace: bool | None = None,
        no_marshal: bool | None = None,
        no_unmarshal: bool | None = None,

        marshaler: Marshaler | None = None,
        marshaler_factory: MarshalerFactory | None = None,
        marshal_as: ta.Any | None = None,
        unmarshaler: Unmarshaler | None = None,
        unmarshaler_factory: UnmarshalerFactory | None = None,
        unmarshal_as: ta.Any | None = None,
) -> dc.field_modifier:
    raise NotImplementedError


globals()['with_field_options'] = _with_field_options


#


def _update_fields_options(
        fields: ta.Iterable[str] | None = None,
        **kwargs: ta.Any,
) -> ta.Callable[[type[T]], type[T]]:
    def inner(a: str, f: dc.Field) -> dc.Field:
        existing = f.metadata.get(FieldOptions, DEFAULT_FIELD_OPTIONS)
        updated = dc.replace(existing, **kwargs)
        return dc.set_field_metadata(f, {FieldOptions: updated})

    return dc.update_fields(inner, fields)


def update_fields_options(
        fields: ta.Iterable[str] | None = None,
        *,
        name: str | None = None,
        alts: ta.Iterable[str] | None = None,

        omit_if: ta.Callable[[ta.Any], bool] | None = None,
        default: lang.Maybe[ta.Any] | None = None,
        embed: bool | None = None,
        generic_replace: bool | None = None,
        no_marshal: bool | None = None,
        no_unmarshal: bool | None = None,

        marshaler: Marshaler | None = None,
        marshaler_factory: MarshalerFactory | None = None,
        marshal_as: ta.Any | None = None,
        unmarshaler: Unmarshaler | None = None,
        unmarshaler_factory: UnmarshalerFactory | None = None,
        unmarshal_as: ta.Any | None = None,
) -> ta.Callable[[type[T]], type[T]]:
    raise NotImplementedError


globals()['update_fields_options'] = _update_fields_options


#


def _update_object_options(
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


def update_object_options(
        cls: type | None = None,
        *,
        field_naming: Naming | None = None,

        ignore_unknown: bool | None = None,
        unwrap_if_single_field: ta.Literal['marshal', 'unmarshal', True, None] = None,

        unknown_field: str | None = None,
        source_field: str | None = None,

        field_defaults: FieldOptions = DEFAULT_FIELD_OPTIONS,
):
    raise NotImplementedError


globals()['update_object_options'] = _update_object_options
