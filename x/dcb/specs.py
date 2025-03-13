import dataclasses as dc
import enum
import typing as ta

from omlish import check
from omlish import lang

from .types import ReprFn


##


class FieldType(enum.Enum):
    INSTANCE = enum.auto()
    CLASS = enum.auto()
    INIT = enum.auto()


@dc.dataclass(frozen=True, kw_only=True)
class FieldSpec:
    name: str
    annotation: ta.Any

    def __post_init__(self) -> None:
        check.non_empty_str(self.name)

    default: lang.Maybe[ta.Any] = lang.empty()
    default_factory: ta.Callable[..., ta.Any] | None = None

    init: bool = True
    repr: bool = True
    hash: ta.Any = None
    compare: bool = True
    metadata: ta.Any = None
    kw_only: lang.Maybe[ta.Any] = lang.empty()

    # doc: ta.Any = None

    repr_fn: ReprFn | None = None

    field_type: FieldType = FieldType.INSTANCE


##


@dc.dataclass(frozen=True, kw_only=True)
class ClassSpec:
    fields: ta.Sequence[FieldSpec]

    @lang.cached_function
    def fields_by_name(self) -> ta.Mapping[str, FieldSpec]:
        dct: dict[str, FieldSpec] = {}
        for f in self.fields:
            check.not_in(f.name, dct)
            dct[f.name] = f
        return dct

    init: bool = True
    repr: bool = True
    eq: bool = True
    order: bool = False
    unsafe_hash: bool = False
    frozen: bool = False

    # match_args: bool = True
    # kw_only: bool = False
    # slots: bool = False
    # weakref_slot: bool = False

    cache_hash: bool = False


##


CLASS_SPEC_ATTR = '__dataclass_spec__'


def get_class_spec(cls: type) -> ClassSpec:
    return check.isinstance(getattr(cls, CLASS_SPEC_ATTR), ClassSpec)
