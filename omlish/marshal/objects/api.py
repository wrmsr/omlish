"""
TODO:
 - @lang.copy_type
"""
import dataclasses as dc
import typing as ta

from ... import check
from ... import lang
from ... import metadata as md
from ...lite.dataclasses import install_dataclass_filtered_repr
from ..api.configs import Config
from ..api.naming import Naming
from ..api.vias import MarshalVia
from ..api.vias import UnmarshalVia


T = ta.TypeVar('T')


##


@ta.final
@install_dataclass_filtered_repr('omit_none')
@dc.dataclass(frozen=True, kw_only=True)
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
    # Custom marshaling

    marshal_via: MarshalVia | None = None
    unmarshal_via: UnmarshalVia | None = None

    ##
    # Validation

    def __post_init__(self) -> None:
        check.isinstance(self.default, (lang.Maybe, None))

        check.isinstance(self.marshal_via, (MarshalVia, None))
        check.isinstance(self.unmarshal_via, (UnmarshalVia, None))

    ##
    # Merging

    def merge(self, *overrides: FieldOptions | None) -> FieldOptions:
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

    ##
    # Type safety

    def __bool__(self) -> ta.NoReturn:
        raise TypeError


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

    @property
    def set(self) -> frozenset[str]:
        try:
            return self._set  # type: ignore[attr-defined]
        except AttributeError:
            pass

        ret = frozenset(v for v in dc.asdict(self).values() if v is not None)

        object.__setattr__(self, '_set', ret)
        return ret


@ta.final
@install_dataclass_filtered_repr('omit_none')
@dc.dataclass(frozen=True, kw_only=True)
class ObjectOptions(Config, lang.Final):
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

    @property
    def specials(self) -> ObjectSpecials:
        try:
            return self._specials  # type: ignore[attr-defined]
        except AttributeError:
            pass

        ret = ObjectSpecials(
            unknown=self.unknown_field,
            source=self.source_field,
        )

        object.__setattr__(self, '_specials', ret)
        return ret

    ##
    # Fields

    field_defaults: FieldOptions = DEFAULT_FIELD_OPTIONS

    fields: ta.Mapping[str | None, FieldOptions] | None = None

    ##
    # Merging

    def merge(self, *overrides: ObjectOptions | None) -> ObjectOptions:
        kw: dict[str, ta.Any] = {}
        for obj in [self, *overrides]:
            if obj is None:
                continue

            for fld in _object_options_fields():
                if (fv := getattr(obj, fld.name)) is None:
                    continue

                if fld.type is FieldOptions:
                    fv = kw.get(fld.name, DEFAULT_FIELD_OPTIONS).merge(fv)

                elif fld.name == 'fields':
                    fd = kw.get('fields') or {}

                    if (nfo := fv.get(None)) is not None:
                        for fn, fo in list(fd.items()):
                            fd[fn] = nfo.merge(fo)
                    nfo = fd.get(None)

                    for fn, fo in fv.items():
                        if fn is None:
                            continue
                        try:
                            xfo = fd[fn]
                        except KeyError:
                            if nfo is not None:
                                fo = nfo.merge(fo)
                            fd[fn] = fo
                        else:
                            fd[fn] = xfo.merge(fo)

                    fv = fd

                kw[fld.name] = fv

        if not kw:
            return self
        return ObjectOptions(**kw)

    ##
    # Type safety

    def __bool__(self) -> ta.NoReturn:
        raise TypeError


@lang.cached_function
def _object_options_fields() -> ta.Sequence[dc.Field]:
    return dc.fields(ObjectOptions)


DEFAULT_OBJECT_OPTIONS = ObjectOptions()


##


@dc.dataclass(frozen=True)
class _ObjectOptionsMetadata(md.ClassDecoratorObjectMetadata, lang.Final):
    opts: ObjectOptions
