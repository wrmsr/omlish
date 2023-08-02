"""
Field:
    name: str | None = None
    type: Any = None
    default: Any | MISSING = MISSING
    default_factory: Any | MISSING = MISSING
    repr: bool = True
    hash: bool | None = None
    init: bool = True
    compare: bool = True
    metadata: Metadata | None = None
    kw_only: bool | MISSING = MISSING

    _field_type: Any = None


Params:
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
"""
import dataclasses as dc
import typing as ta

from omlish import lang

from .internals import Params
from .internals import PARAMS_ATTR


def get_params(obj: ta.Any) -> Params:
    if dc.is_dataclass(obj):
        return getattr(obj, PARAMS_ATTR)
    raise TypeError(obj)


@dc.dataclass(frozen=True)
class FieldExtras(lang.Final):
    coerce: ta.Optional[ta.Union[bool, ta.Callable[[ta.Any], ta.Any]]] = None


@dc.dataclass(frozen=True)
class Params12(lang.Final):
    match_args: bool = True
    kw_only: bool = False
    slots: bool = False
    weakref_slot: bool = False


@dc.dataclass(frozen=True)
class ParamsExtras(lang.Final):
    metadata: ta.Optional[ta.Mapping[ta.Any, ta.Any]] = None
