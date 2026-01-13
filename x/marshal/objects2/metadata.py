import typing as ta

from omlish import cached
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang
from omlish.marshal.base.types import Marshaler
from omlish.marshal.base.types import MarshalerFactory
from omlish.marshal.base.types import Unmarshaler
from omlish.marshal.base.types import UnmarshalerFactory
from omlish.marshal.naming import Naming


##


@dc.dataclass(frozen=True, kw_only=True)
class FieldMetadata:
    """
    Unified field metadata - all configuration for a single field's marshaling/unmarshaling.

    This is the single source of truth for field configuration, merging what used to be split
    between FieldOptions and FieldMetadata in the old design.
    """

    # Naming
    name: str | None = None
    alts: ta.Iterable[str] | None = None

    # Behavior options
    omit_if: ta.Callable[[ta.Any], bool] | None = None
    default: lang.Maybe[ta.Any] = dc.xfield(default=lang.empty(), check_type=lang.Maybe)
    embed: bool = False
    generic_replace: bool = False
    no_marshal: bool = False
    no_unmarshal: bool = False

    # Custom handlers
    marshaler: Marshaler | None = dc.xfield(None, check_type=(Marshaler, None))
    marshaler_factory: MarshalerFactory | None = None
    unmarshaler: Unmarshaler | None = dc.xfield(None, check_type=(Unmarshaler, None))
    unmarshaler_factory: UnmarshalerFactory | None = None

    def merge(self, override: 'FieldMetadata | None') -> 'FieldMetadata':
        """
        Merge this metadata with an override, where the override takes precedence.

        For each field:
        - If override has a non-default value, use it
        - Otherwise, keep the current value

        This is explicit and clear, no magic kwargs splitting.
        """

        if override is None:
            return self

        # Build kwargs for fields that override provides
        kw: dict[str, ta.Any] = {}

        for field in dc.fields(FieldMetadata):
            override_val = getattr(override, field.name)

            # Get the default value for this field
            if field.default_factory is not dc.MISSING:
                default_val = field.default_factory()
            elif field.default is not dc.MISSING:
                default_val = field.default
            else:
                # No default - shouldn't happen for our fields
                default_val = None

            # Use override value if it differs from default
            if override_val != default_val:
                kw[field.name] = override_val
            else:
                # Keep current value
                kw[field.name] = getattr(self, field.name)

        return FieldMetadata(**kw)


DEFAULT_FIELD_METADATA = FieldMetadata()


@dc.dataclass(frozen=True, kw_only=True)
class ObjectMetadata:
    """Object-level marshaling metadata."""

    field_naming: Naming | None = None

    unknown_field: str | None = None
    source_field: str | None = None

    @cached.property
    def specials(self) -> 'ObjectSpecials':
        return ObjectSpecials(
            unknown=self.unknown_field,
            source=self.source_field,
        )

    field_defaults: FieldMetadata = DEFAULT_FIELD_METADATA

    ignore_unknown: bool = False


@dc.dataclass(frozen=True, kw_only=True)
class ObjectSpecials:
    """Special field names for an object."""

    unknown: str | None = None
    source: str | None = None

    @cached.property
    def set(self) -> frozenset[str]:
        return frozenset(v for v in dc.asdict(self).values() if v is not None)


##


@dc.dataclass(frozen=True, kw_only=True)
class FieldInfo:
    """
    Computed field information - derived from FieldMetadata + dataclass introspection.

    This is purely derived/computed data, not configuration. The metadata field contains
    the final merged configuration.
    """

    name: str
    type: ta.Any

    marshal_name: str | None
    unmarshal_names: ta.Sequence[str]

    metadata: FieldMetadata = DEFAULT_FIELD_METADATA


@dc.dataclass(frozen=True)
class FieldInfos:
    """Collection of field infos with convenient lookups."""

    lst: ta.Sequence[FieldInfo]

    def __iter__(self) -> ta.Iterator[FieldInfo]:
        return iter(self.lst)

    def __len__(self) -> int:
        return len(self.lst)

    @cached.property
    @dc.init
    def by_name(self) -> ta.Mapping[str, FieldInfo]:
        return col.make_map(((fi.name, fi) for fi in self), strict=True)

    @cached.property
    @dc.init
    def by_marshal_name(self) -> ta.Mapping[str, FieldInfo]:
        return col.make_map(((fi.marshal_name, fi) for fi in self if fi.marshal_name is not None), strict=True)

    @cached.property
    @dc.init
    def by_unmarshal_name(self) -> ta.Mapping[str, FieldInfo]:
        return col.make_map(((n, fi) for fi in self for n in fi.unmarshal_names), strict=True)
