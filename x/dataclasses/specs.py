"""Should be kept pure. No references to dc std, no references to impl detail."""
import dataclasses as dc
import enum
import typing as ta

from omlish import check
from omlish import lang


##


CoerceFn: ta.TypeAlias = ta.Callable[[ta.Any], ta.Any]
ValidateFn: ta.TypeAlias = ta.Callable[[ta.Any], bool]
ReprFn: ta.TypeAlias = ta.Callable[[ta.Any], str | None]

InitFn: ta.TypeAlias = ta.Callable[[ta.Any], None]
ClassValidateFn: ta.TypeAlias = ta.Callable[..., bool]


class DefaultFactory(ta.NamedTuple):
    fn: ta.Callable[..., ta.Any]


##


class FieldType(enum.StrEnum):
    INSTANCE = enum.auto()
    CLASS_VAR = enum.auto()
    INIT_VAR = enum.auto()

    __repr__ = lang.enum_name_repr


@dc.dataclass(frozen=True, kw_only=True, eq=False)
class FieldSpec(lang.Final):
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

    # doc: ta.Any = None

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
            raise ValueError(f'mutable default {type(dfv)} for field {self.name} is not allowed: use default_factory')


##


@dc.dataclass(frozen=True, kw_only=True, eq=False)
class ClassSpec(lang.Final):
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

    metadata: ta.Mapping[ta.Any, ta.Any] | None = None

    reorder: bool = False
    cache_hash: bool = False
    generic_init: bool = False
    override: bool = False
    repr_id: bool = False

    ## callbacks
    #

    init_fns: ta.Sequence[InitFn | property] | None = None

    @dc.dataclass(frozen=True)
    class ValidateFnWithParams:
        fn: ClassValidateFn
        params: ta.Sequence[str]

        def __post_init__(self) -> None:
            check.not_isinstance(self.params, str)

    validate_fns: ta.Sequence[ValidateFnWithParams] | None = None

    ## validate
    #

    def __post_init__(self) -> None:
        dct: dict[str, FieldSpec] = {}
        for f in self.fields:
            check.not_in(f.name, dct)
            dct[f.name] = f
        object.__setattr__(self, '_fields_by_name', dct)

        if self.order and not self.eq:
            raise ValueError('eq must be true if order is true')
