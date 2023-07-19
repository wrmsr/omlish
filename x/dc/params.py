import dataclasses as dc
import typing as ta

from omlish import lang

from .internals import DataclassParams
from .internals import FieldType


EX_PARAMS_ATTR = '__dataclass_ex_params__'


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
    kw_only: lang.Maybe[ta.Any] = lang.empty()

    field_type: FieldType = FieldType.INSTANCE


def ex_field(obj: ta.Any) -> ExField:
    if isinstance(obj, ExField):
        return obj
    if isinstance(obj, dc.Field):
        return obj.metadata[ExField]
    raise TypeError(obj)


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


def ex_params(obj: ta.Any) -> ExParams:
    if isinstance(obj, ExParams):
        return obj
    if isinstance(obj, DataclassParams):
        return obj.metadata[ExParams]
    if dc.is_dataclass(obj):
        return getattr(obj, EX_PARAMS_ATTR)
    raise TypeError(obj)
