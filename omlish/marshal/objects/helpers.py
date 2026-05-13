# ruff: noqa: UP037
"""
This file is considered part of the marshal api, and must be diligent about not importing too much like the rest of the
api modules. Specifically, it can't eagerly import `omlish.dataclasses` (even though `dc.set_field_metadata` itself
tries to only lazily load heavy dataclass internals).
"""
import typing as ta

from ... import lang
from ..api.naming import Naming
from ..api.vias import MarshalVia
from ..api.vias import UnmarshalVia
from .api import DEFAULT_FIELD_OPTIONS
from .api import FieldOptions
from .api import ObjectOptions
from .api import _ObjectOptionsMetadata


with lang.auto_proxy_import(globals()):
    from ... import dataclasses as dc


T = ta.TypeVar('T')


##
# The following functions duplicate kwargs/defaults from the api objects, but does so only for autocomplete - the
# underlying impl blindly forwards given kwargs to allow distinction between `None` and absent.


def _dc_field_options(
        **kwargs: ta.Any,
) -> 'dc.field_modifier':
    @dc.field_modifier
    def inner(f: dc.Field) -> dc.Field:
        existing = f.metadata.get(FieldOptions, DEFAULT_FIELD_OPTIONS)
        updated = dc.replace(existing, **kwargs)
        return dc.set_field_metadata(f, {FieldOptions: updated})

    return inner


def dc_field_options(
        name: str | None = None,
        alts: ta.Iterable[str] | None = None,

        omit_if: ta.Callable[[ta.Any], bool] | None = None,
        default: lang.Maybe[ta.Any] | None = None,
        embed: bool | None = None,
        generic_replace: bool | None = None,
        no_marshal: bool | None = None,
        no_unmarshal: bool | None = None,

        marshal_via: MarshalVia | None = None,
        unmarshal_via: UnmarshalVia | None = None,
) -> 'dc.field_modifier':
    raise NotImplementedError


globals()['dc_field_options'] = _dc_field_options


#


def _update_field_options(
        field: str | ta.Iterable[str] | None = None,
        **kwargs: ta.Any,
) -> ta.Callable[[type[T]], type[T]]:
    fo = FieldOptions(**kwargs)

    if field is None or isinstance(field, str):
        fd: dict = {field: fo}
    else:
        fd = {f: fo for f in field}

    oo = ObjectOptions(fields=fd)

    def inner(cls):
        return _ObjectOptionsMetadata(oo)(cls)

    return inner


def update_field_options(
        field: str | ta.Iterable[str] | None = None,
        *,
        name: str | None = None,
        alts: ta.Iterable[str] | None = None,

        omit_if: ta.Callable[[ta.Any], bool] | None = None,
        default: lang.Maybe[ta.Any] | None = None,
        embed: bool | None = None,
        generic_replace: bool | None = None,
        no_marshal: bool | None = None,
        no_unmarshal: bool | None = None,

        marshal_via: MarshalVia | None = None,
        unmarshal_via: UnmarshalVia | None = None,
) -> ta.Callable[[type[T]], type[T]]:
    raise NotImplementedError


globals()['update_field_options'] = _update_field_options


#


def _update_object_options(
        cls: type | None = None,
        **kwargs: ta.Any,
):
    oo = ObjectOptions(**kwargs)

    def inner(cls):
        return _ObjectOptionsMetadata(oo)(cls)

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
