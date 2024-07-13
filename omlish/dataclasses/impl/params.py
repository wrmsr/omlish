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

from ... import lang
from .internals import PARAMS_ATTR
from .internals import Params
from .metadata import EMPTY_METADATA
from .metadata import METADATA_ATTR


##


@dc.dataclass(frozen=True)
class FieldExtras(lang.Final):
    coerce: bool | ta.Callable[[ta.Any], ta.Any] | None = None
    check: ta.Callable[[ta.Any], bool] | None = None
    check_type: bool | None = None
    override: bool = False
    repr_fn: ta.Callable[[ta.Any], str | None] | None = None


DEFAULT_FIELD_EXTRAS = FieldExtras()


def get_field_extras(f: dc.Field) -> FieldExtras:
    if not isinstance(f, dc.Field):
        raise TypeError(f)
    return f.metadata.get(FieldExtras, DEFAULT_FIELD_EXTRAS)


##


def get_params_cls(obj: ta.Any) -> type | None:
    if not isinstance(obj, type):
        obj = type(obj)
    for cur in obj.__mro__:
        if PARAMS_ATTR in cur.__dict__:
            return cur
    return None


def get_params(obj: ta.Any) -> Params:
    if not hasattr(obj, PARAMS_ATTR):
        raise TypeError(obj)
    return getattr(obj, PARAMS_ATTR)


##


@dc.dataclass(frozen=True)
class ParamsExtras(lang.Final):
    reorder: bool = False
    cache_hash: bool = False
    generic_init: bool = False


DEFAULT_PARAMS_EXTRAS = ParamsExtras()


def get_params_extras(obj: ta.Any) -> ParamsExtras:
    if (pcls := get_params_cls(obj)) is None:
        raise TypeError(pcls)

    md = pcls.__dict__.get(METADATA_ATTR, EMPTY_METADATA)
    return md.get(ParamsExtras, DEFAULT_PARAMS_EXTRAS)


##


@dc.dataclass(frozen=True)
class MetaclassParams:
    confer: frozenset[str] = frozenset()


DEFAULT_METACLASS_PARAMS = MetaclassParams()


def get_metaclass_params(obj: ta.Any) -> MetaclassParams:
    if (pcls := get_params_cls(obj)) is None:
        raise TypeError(pcls)

    md = pcls.__dict__.get(METADATA_ATTR, EMPTY_METADATA)
    return md.get(MetaclassParams, DEFAULT_METACLASS_PARAMS)
