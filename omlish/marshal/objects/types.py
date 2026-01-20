import typing as ta

from ... import cached
from ... import dataclasses as dc
from ... import lang
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.types import Unmarshaler
from ..base.types import UnmarshalerFactory
from ..naming import Naming


##


@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(default_repr_fn=lang.opt_repr)
class FieldOptions:
    """
    Unified field options - all configuration for a single field's marshaling/unmarshaling.

    This is the single source of truth for field configuration, merging what used to be split between FieldOptions and
    FieldMetadata in the old design.
    """

    ##
    # Naming

    name: str | None = None
    alts: ta.Iterable[str] | None = None

    ##
    # Behavior options

    omit_if: ta.Callable[[ta.Any], bool] | None = None

    default: lang.Maybe[ta.Any] | None = dc.xfield(default=None, check_type=(lang.Maybe, None))

    embed: bool | None = None

    generic_replace: bool | None = None

    no_marshal: bool | None = None
    no_unmarshal: bool | None = None

    ##
    # Custom handlers

    marshaler: Marshaler | None = dc.xfield(None, check_type=(Marshaler, None))
    marshaler_factory: MarshalerFactory | None = None

    unmarshaler: Unmarshaler | None = dc.xfield(None, check_type=(Unmarshaler, None))
    unmarshaler_factory: UnmarshalerFactory | None = None

    ##
    # Merging

    def merge(self, *overrides: ta.Optional['FieldOptions']) -> 'FieldOptions':
        kw: dict[str, ta.Any] = {}
        for obj in [self, *overrides]:
            if obj is None:
                continue

            for fld in _field_options_fields():
                if (fv := getattr(obj, fld.name)) is None:
                    continue

                kw[fld.name] = fv

        if not kw:
            return self
        return FieldOptions(**kw)


@lang.cached_function
def _field_options_fields() -> ta.Sequence[dc.Field]:
    return dc.fields(FieldOptions)


DEFAULT_FIELD_OPTIONS = FieldOptions()


##


@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(default_repr_fn=lang.opt_repr)
class ObjectSpecials:
    """Special field names for an object."""

    unknown: str | None = None
    source: str | None = None

    @cached.property
    def set(self) -> frozenset[str]:
        return frozenset(v for v in dc.asdict(self).values() if v is not None)


@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(default_repr_fn=lang.opt_repr)
class ObjectOptions:
    """Object-level marshaling options."""

    ##
    # Naming

    field_naming: Naming | None = None

    ##
    # Behavior options

    ignore_unknown: bool = False

    ##
    # Special fields

    unknown_field: str | None = None
    source_field: str | None = None

    @cached.property
    def specials(self) -> ObjectSpecials:
        return ObjectSpecials(
            unknown=self.unknown_field,
            source=self.source_field,
        )

    ##
    # Field defaults

    field_defaults: FieldOptions = DEFAULT_FIELD_OPTIONS

    ##
    # Merging

    def merge(self, *overrides: ta.Optional['ObjectOptions']) -> 'ObjectOptions':
        kw: dict[str, ta.Any] = {}
        for obj in [self, *overrides]:
            if obj is None:
                continue

            for fld in _object_options_fields():
                if (fv := getattr(obj, fld.name)) is None:
                    continue

                if fld.type is FieldOptions:
                    fv = kw.get(fld.name, DEFAULT_FIELD_OPTIONS).merge(fv)

                kw[fld.name] = fv

        if not kw:
            return self
        return ObjectOptions(**kw)


@lang.cached_function
def _object_options_fields() -> ta.Sequence[dc.Field]:
    return dc.fields(ObjectOptions)


DEFAULT_OBJECT_OPTIONS = ObjectOptions()
