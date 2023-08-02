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
import sys
import typing as ta

from omlish import lang

from .metadata import get_metadata
from .internals import Params
from .internals import PARAMS_ATTR


IS_12 = sys.version_info[1] >= 12


##


@dc.dataclass(frozen=True)
class FieldExtras(lang.Final):
    coerce: ta.Optional[ta.Union[bool, ta.Callable[[ta.Any], ta.Any]]] = None


##


def get_params(obj: ta.Any) -> Params:
    if hasattr(obj, PARAMS_ATTR):
        return getattr(obj, PARAMS_ATTR)
    raise TypeError(obj)
##


@dc.dataclass(frozen=True)
class Params12(lang.Final):
    match_args: bool = True
    kw_only: bool = False
    slots: bool = False
    weakref_slot: bool = False


DEFAULT_PARAMS12 = Params12()


def get_params12(obj: ta.Any) -> Params12:
    p = get_params(obj)
    if IS_12:
        return Params12(
            match_args=p.match_args,
            kw_only=p.kw_only,
            slots=p.slots,
            weakref_slot=p.weakref_slot,
        )

    md = get_metadata(obj)
    if (md_p12 := md.get(Params12)) is not None:
        return md_p12

    return DEFAULT_PARAMS12


##


@dc.dataclass(frozen=True)
class ParamsExtras(lang.Final):
    reorder: bool = False
