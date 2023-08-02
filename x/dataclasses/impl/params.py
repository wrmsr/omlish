import dataclasses as dc
import sys
import typing as ta

from omlish import lang

from .internals import FieldType
from .internals import PARAMS_ATTR
from .internals import Params


IS_12 = sys.version_info[1] >= 12

MISSING = dc.MISSING

EX_PARAMS_ATTR = '__dataclass_ex_params__'
EX_FIELDS_ATTR = '__dataclass_ex_fields__'


##


@dc.dataclass()
class ExField:
    name: ta.Optional[str] = None
    type: ta.Any = None
    default: lang.Maybe[ta.Any] = lang.empty()
    default_factory: lang.Maybe[ta.Any] = lang.empty()
    repr: bool = True
    hash: ta.Optional[bool] = None
    init: bool = True
    compare: bool = True
    metadata: ta.Optional[ta.Mapping[ta.Any, ta.Any]] = None
    kw_only: ta.Optional[bool] = None

    field_type: FieldType = FieldType.INSTANCE

    base: ta.Optional[dc.Field] = None


def make_ex_field(f: dc.Field) -> ExField:
    return ExField(
        default=lang.just(f.default) if f.default is not MISSING else lang.empty(),
        default_factory=lang.just(f.default_factory) if f.default_factory is not MISSING else lang.empty(),
        init=f.init,
        repr=f.repr,
        hash=f.hash,
        compare=f.compare,
        metadata=f.metadata,
        kw_only=f.kw_only if f.kw_only is not MISSING else None,

        field_type=FieldType.INSTANCE if (ft := getattr(f, '_field_type')) is None else FieldType[ft],

        base=f,
    )


def ex_field(obj: ta.Any) -> ExField:
    if isinstance(obj, ExField):
        return obj
    if isinstance(obj, dc.Field):
        return obj.metadata[ExField]
    raise TypeError(obj)


def ex_fields(class_or_instance: ta.Any) -> ta.Sequence[ExField]:
    try:
        fields = getattr(class_or_instance, EX_FIELDS_ATTR)
    except AttributeError:
        raise TypeError('must be called with a dataclass type or instance') from None
    # order, so the order of the tuple is as the fields were defined.
    return tuple(f for f in fields.values() if f.field_type is FieldType.INSTANCE)


##


@dc.dataclass()
class ExParams:
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

    base: ta.Optional[Params] = None


def make_ex_params(p: Params) -> ExParams:
    return ExParams(
        init=p.init,
        repr=p.repr,
        eq=p.eq,
        order=p.order,
        unsafe_hash=p.unsafe_hash,
        frozen=p.frozen,

        **(dict(
            match_args=p.match_args,
            kw_only=p.kw_only,
            slots=p.slots,
            weakref_slot=p.weakref_slot,
        ) if IS_12 else {}),

        base=p,
    )


def params(obj: ta.Any) -> Params:
    if dc.is_dataclass(obj):
        return getattr(obj, PARAMS_ATTR)
    raise TypeError(obj)


def ex_params(obj: ta.Any) -> ExParams:
    if isinstance(obj, ExParams):
        return obj
    if isinstance(obj, Params):
        return obj.metadata[ExParams]
    if dc.is_dataclass(obj):
        return getattr(obj, EX_PARAMS_ATTR)
    raise TypeError(obj)
