"""
FIXME:
 - make_dataclass

TODO:
 - default_fn
  - toposort
 - type_check
 - coerce
 - Optional/Sequence/AbstractSet/Mapping unpacking
 - init/check/validate
 - reorder? tools hate it
  - x: int = dc.field(default=dc.REQUIRED) - kwonly but better than nothing

Backport:
 - dc:
  - match_args=True
  - kw_only=False
  - slots=False
  - weakref_slot=False
 - field:
  - kw_only=MISSING
"""
import dataclasses as dc
import typing as ta

from .. import lang


class Check(lang.Marker):
    pass


def field(
        *,
        default=dc.MISSING,
        default_factory=dc.MISSING,
        init=True,
        repr=True,
        hash=None,
        compare=True,
        metadata=None,

        kw_only=False,

        check: ta.Optional[ta.Callable[[ta.Any], bool]] = None,
):
    md = {**(metadata or {})}

    if check is not None:
        if Check in md:
            raise KeyError(md)
        md[Check] = check

    fld = dc.field(  # type: ignore
        default=default,
        default_factory=default_factory,
        init=init,
        repr=repr,
        hash=hash,
        compare=compare,
        metadata=md,
    )
    return fld


class Params(ta.NamedTuple):
    init: bool
    repr: bool
    eq: bool
    order: bool
    unsafe_hash: bool
    frozen: bool


def process_class(cls: type, params: Params) -> type:
    dcls = dc.dataclass(  # type: ignore
        cls,
        init=params.init,
        repr=params.repr,
        eq=params.eq,
        order=params.order,
        unsafe_hash=params.unsafe_hash,
        frozen=params.frozen,
    )
    return dcls


def dataclass(
        cls=None,
        /,
        *,
        init=True,
        repr=True,
        eq=True,
        order=False,
        unsafe_hash=False,
        frozen=False,
):
    def wrap(cls):
        return process_class(cls, Params(
            init=init,
            repr=repr,
            eq=eq,
            order=order,
            unsafe_hash=unsafe_hash,
            frozen=frozen,
        ))

    if cls is None:
        return wrap
    return wrap(cls)
