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
import dataclasses as _dc
import typing as ta

from .lang import Marker as _Marker


Field = _dc.Field
FrozenInstanceError = _dc.FrozenInstanceError
InitVar = _dc.InitVar
MISSING = _dc.MISSING

fields = _dc.fields
asdict = _dc.asdict
astuple = _dc.astuple
make_dataclass = _dc.make_dataclass
replace = _dc.replace
is_dataclass = _dc.is_dataclass


class _Check(_Marker):
    pass


def _field(
        *,
        default=MISSING,
        default_factory=MISSING,
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
        if _Check in md:
            raise KeyError(md)
        md[_Check] = check

    fld = _dc.field(  # type: ignore
        default=default,
        default_factory=default_factory,
        init=init,
        repr=repr,
        hash=hash,
        compare=compare,
        metadata=md,
    )
    return fld


class _Params(ta.NamedTuple):
    init: bool
    repr: bool
    eq: bool
    order: bool
    unsafe_hash: bool
    frozen: bool


def _process_class(cls: type, params: _Params) -> type:
    dcls = _dc.dataclass(  # type: ignore
        cls,
        init=params.init,
        repr=params.repr,
        eq=params.eq,
        order=params.order,
        unsafe_hash=params.unsafe_hash,
        frozen=params.frozen,
    )
    return dcls


def _dataclass(
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
        return _process_class(cls, _Params(
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


from dataclasses import dataclass  # noqa


globals()['dataclass'] = _dataclass

field = _field
