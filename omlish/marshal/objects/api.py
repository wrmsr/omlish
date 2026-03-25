"""
TODO:
 - @lang.copy_type
"""
import typing as ta

from ... import cached
from ... import check
from ... import dataclasses as dc
from ... import lang
from ..api.naming import Naming
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory


T = ta.TypeVar('T')


##


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(default_repr_fn=lang.opt_repr)
class FieldOptions(lang.Final):
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

    default: lang.Maybe[ta.Any] | None = None

    embed: bool | None = None

    generic_replace: bool | None = None

    no_marshal: bool | None = None
    no_unmarshal: bool | None = None

    ##
    # Custom handlers

    marshaler: Marshaler | None = None
    marshaler_factory: MarshalerFactory | None = None
    marshal_as: ta.Any | None = None

    unmarshaler: Unmarshaler | None = None
    unmarshaler_factory: UnmarshalerFactory | None = None
    unmarshal_as: ta.Any | None = None

    ##
    # Validation

    def __post_init__(self) -> None:
        check.isinstance(self.default, (lang.Maybe, None))

        check.isinstance(self.marshaler, (Marshaler, None))
        check.isinstance(self.unmarshaler, (Unmarshaler, None))

        for mutex_atts in [
            ('marshaler', 'marshaler_factory', 'marshal_as'),
            ('unmarshaler', 'unmarshaler_factory', 'unmarshal_as'),
        ]:
            set_atts = [a for a in mutex_atts if getattr(self, a) is not None]
            if len(set_atts) > 1:
                raise ValueError(f'Cannot set {set_atts} at the same time')

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


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
class ObjectSpecials(lang.Final):
    """Special field names for an object."""

    unknown: str | None = None
    source: str | None = None

    @cached.property
    def set(self) -> frozenset[str]:
        return frozenset(v for v in dc.asdict(self).values() if v is not None)


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(default_repr_fn=lang.opt_repr)
class ObjectOptions(lang.Final):
    """Object-level marshaling options."""

    ##
    # Naming

    field_naming: Naming | None = None

    ##
    # Behavior options

    ignore_unknown: bool | None = None

    unwrap_if_single_field: ta.Literal['marshal', 'unmarshal', True, None] = None

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
