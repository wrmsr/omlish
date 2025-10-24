"""Should be kept pure. No references to dc std, no references to impl detail."""
import dataclasses as dc
import enum
import types
import typing as ta

from .. import check
from .. import lang


T = ta.TypeVar('T')


##


CoerceFn: ta.TypeAlias = ta.Callable[[ta.Any], ta.Any]
ValidateFn: ta.TypeAlias = ta.Callable[[ta.Any], bool]
ReprFn: ta.TypeAlias = ta.Callable[[ta.Any], str | None]

InitFn: ta.TypeAlias = ta.Callable[[ta.Any], None]
ClassValidateFn: ta.TypeAlias = ta.Callable[..., bool]


class DefaultFactory(ta.NamedTuple):
    fn: ta.Callable[..., ta.Any]


##


class _SpecBase:
    _BOOL_FIELDS: ta.ClassVar[ta.Sequence[dc.Field]]
    _OPT_BOOL_FIELDS: ta.ClassVar[ta.Sequence[dc.Field]]

    def _check_spec_base_fields(self) -> None:
        for f in self._BOOL_FIELDS:
            if not isinstance(bv := getattr(self, f.name), bool):
                raise TypeError(f'dataclass {self.__class__.__name__} attr {f.name} must be bool, got {bv!r}')

        for f in self._OPT_BOOL_FIELDS:
            if not isinstance(bv := getattr(self, f.name), (bool, types.NoneType)):
                raise TypeError(f'dataclass {self.__class__.__name__} attr {f.name} must be bool or None, got {bv!r}')


def _init_spec_base(cls):
    cls._BOOL_FIELDS = [f for f in dc.fields(cls) if f.type is bool]  # noqa
    cls._OPT_BOOL_FIELDS = [f for f in dc.fields(cls) if f.type in (bool | None, ta.Optional[bool])]  # noqa

    return cls


##


class FieldType(enum.StrEnum):
    INSTANCE = enum.auto()
    CLASS_VAR = enum.auto()
    INIT_VAR = enum.auto()

    __repr__ = lang.enum_name_repr


@_init_spec_base
@dc.dataclass(frozen=True, kw_only=True, eq=False)
class FieldSpec(_SpecBase, lang.Final):
    name: str
    annotation: ta.Any

    default: lang.Maybe[DefaultFactory | ta.Any] = lang.empty()

    ##
    # std

    init: bool = True
    repr: bool = True

    # This can be a bool or None. If true, this field is included in the generated __hash__() method. If false, this
    # field is excluded from the generated __hash__(). If None (the default), use the value of compare: this would
    # normally be the expected behavior, since a field should be included in the hash if it's used for comparisons.
    # Setting this value to anything other than None is discouraged.
    hash: bool | None = None  # FIXME: type?

    compare: bool = True

    # This can be a mapping or None. None is treated as an empty dict. This value is wrapped in MappingProxyType() to
    # make it read-only, and exposed on the Field object. It is not used at all by Data Classes, and is provided as a
    # third-party extension mechanism. Multiple third-parties can each have their own key, to use as a namespace in the
    # metadata.
    metadata: ta.Mapping[ta.Any, ta.Any] | None = None

    kw_only: bool | None = None

    doc: ta.Any = None

    ##
    # ext

    # derive: ta.Callable[..., ta.Any] | None = None  # NYI in core

    coerce: bool | CoerceFn | None = None
    validate: ValidateFn | None = None
    check_type: bool | type | tuple[type | None, ...] | None = None

    override: bool = False

    repr_fn: ReprFn | None = None
    repr_priority: int | None = None

    # frozen: bool | None = None  # NYI in core

    ##
    # derived

    field_type: FieldType = FieldType.INSTANCE

    ##
    # validate

    def __post_init__(self) -> None:
        check.non_empty_str(self.name)
        check.arg(self.name.isidentifier())

        self._check_spec_base_fields()

        if self.field_type in (FieldType.CLASS_VAR, FieldType.INIT_VAR):
            if isinstance(self.default.or_else(None), DefaultFactory):
                raise TypeError(f'field {self.name} cannot have a default factory')

        if self.field_type is FieldType.CLASS_VAR:
            if self.kw_only is not None:
                raise TypeError(f'field {self.name} is a ClassVar but specifies kw_only')
            check.none(self.coerce)
            check.none(self.validate)
            check.in_(self.check_type, (None, False))

        if (
                self.field_type is FieldType.INSTANCE and
                self.default.present and
                not isinstance(dfv := self.default.must(), DefaultFactory) and
                dfv.__class__.__hash__ is None  # noqa
        ):
            raise ValueError(
                f'mutable default {type(dfv)} for field {self.name} '
                f'is not allowed: use default_factory',
            )


##


@_init_spec_base
@dc.dataclass(frozen=True, kw_only=True, eq=False)
class ClassSpec(_SpecBase, lang.Final):
    ##
    # fields

    fields: ta.Sequence[FieldSpec]

    @property
    def fields_by_name(self) -> ta.Mapping[str, FieldSpec]:
        return self._fields_by_name

    _fields_by_name: ta.ClassVar[ta.Mapping[str, FieldSpec]]

    ##
    # std

    init: bool = True
    repr: bool = True
    eq: bool = True
    order: bool = False
    unsafe_hash: bool = False
    frozen: bool = False

    match_args: bool = True
    kw_only: bool = False
    slots: bool = False
    weakref_slot: bool = False

    ##
    # ext

    metadata: ta.Sequence[ta.Any] | None = None

    @property
    def metadata_by_type(self) -> ta.Mapping[type, ta.Sequence[ta.Any]]:
        return self._metadata_by_type

    _metadata_by_type: ta.ClassVar[ta.Mapping[type, ta.Sequence[ta.Any]]]

    @ta.overload
    def get_last_metadata(self, ty: type[T], default: T) -> T:
        ...

    @ta.overload
    def get_last_metadata(self, ty: type[T], default: None = None) -> T | None:
        ...

    def get_last_metadata(self, ty, default=None):
        try:
            mdl = self._metadata_by_type[ty]
        except KeyError:
            return default
        if not mdl:
            return default
        return mdl[-1]

    #

    reorder: bool = False
    cache_hash: bool = False
    generic_init: bool = False
    override: bool = False
    allow_dynamic_dunder_attrs: bool = False

    repr_id: bool = False
    terse_repr: bool = False
    default_repr_fn: ReprFn | None = None

    allow_redundant_decorator: bool = False

    ##
    # callbacks

    init_fns: ta.Sequence[InitFn | property] | None = None

    @dc.dataclass(frozen=True)
    class ValidateFnWithParams:
        fn: ClassValidateFn
        params: ta.Sequence[str]

        def __post_init__(self) -> None:
            check.not_isinstance(self.params, str)

    validate_fns: ta.Sequence[ValidateFnWithParams] | None = None

    ##
    # validate

    def __post_init__(self) -> None:
        self._check_spec_base_fields()

        fields_by_name: dict[str, FieldSpec] = {}
        for f in self.fields:
            check.not_in(f.name, fields_by_name)
            fields_by_name[f.name] = f
        object.__setattr__(self, '_fields_by_name', fields_by_name)

        metadata_by_type: dict[type, list[ta.Any]] = {}
        for md in self.metadata or ():
            mdt = type(md)
            try:
                mdl = metadata_by_type[mdt]
            except KeyError:
                mdl = metadata_by_type[mdt] = []
            mdl.append(md)
        object.__setattr__(self, '_metadata_by_type', metadata_by_type)

        if self.order and not self.eq:
            raise ValueError('eq must be true if order is true')
