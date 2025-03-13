import dataclasses as dc
import enum
import typing as ta

from omlish import check
from omlish import lang

from .types import InitFn
from .types import ReprFn
from .types import ValidateFn


##


class FieldType(enum.Enum):
    INSTANCE = enum.auto()
    CLASS = enum.auto()
    INIT = enum.auto()


@dc.dataclass(frozen=True, kw_only=True)
class FieldSpec:
    name: str
    annotation: ta.Any

    ##
    # defaults

    default: lang.Maybe[ta.Any] = lang.empty()
    default_factory: ta.Callable[..., ta.Any] | None = None

    @property
    def has_default(self) -> bool:
        return self.default.present or self.default_factory is not None

    ##
    # std

    init: bool = True
    repr: bool = True
    hash: ta.Any = None
    compare: bool = True
    metadata: ta.Any = None
    kw_only: lang.Maybe[ta.Any] = lang.empty()

    # doc: ta.Any = None

    ##
    # ext

    # derive: ta.Callable[..., ta.Any] | None = None
    # coerce: bool | ta.Callable[[ta.Any], ta.Any] | None = None
    # validate: ta.Callable[[ta.Any], bool] | None = None
    # check_type: bool | type | tuple[type | None, ...] | None = None
    override: bool = False
    repr_fn: ReprFn | None = None
    # frozen: bool | None = None

    ##
    # derived

    field_type: FieldType = FieldType.INSTANCE

    ##
    # init

    def __post_init__(self) -> None:
        check.non_empty_str(self.name)

        check.state(not (self.default.present and self.default_factory is not None))



##


@dc.dataclass(frozen=True, kw_only=True)
class ClassSpec:
    ##
    # fields

    fields: ta.Sequence[FieldSpec]

    @lang.cached_function
    def fields_by_name(self) -> ta.Mapping[str, FieldSpec]:
        dct: dict[str, FieldSpec] = {}
        for f in self.fields:
            check.not_in(f.name, dct)
            dct[f.name] = f
        return dct

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
    # slots: bool = False
    # weakref_slot: bool = False

    ##
    # ext

    metadata = None

    reorder: bool = False
    cache_hash: bool = False
    # generic_init = MISSING,
    override: bool = False

    ## callbacks
    #

    init_fns: ta.Sequence[InitFn] | None = None

    @dc.dataclass(frozen=True)
    class ValidateFnWithParams:
        fn: ValidateFn
        params: ta.Sequence[str]

        def __post_init__(self) -> None:
            check.not_isinstance(self.params, str)

    validate_fns: ta.Sequence[ValidateFnWithParams] | None = None


##


CLASS_SPEC_ATTR = '__dataclass_spec__'


def get_class_spec(cls: type) -> ClassSpec:
    return check.isinstance(getattr(cls, CLASS_SPEC_ATTR), ClassSpec)
