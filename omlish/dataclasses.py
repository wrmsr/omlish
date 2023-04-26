"""
TODO:
 - default_fn
  - toposort
 - type_check
 - coerce
 - init/check/validate

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
):
    return _dc.field(
        default=default,
        default_factory=default_factory,
        init=init,
        repr=repr,
        hash=hash,
        compare=compare,
        metadata=metadata,
    )


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
    return _dc.dataclass(
        cls,
        init=init,
        repr=repr,
        eq=eq,
        order=order,
        unsafe_hash=unsafe_hash,
        frozen=frozen,
    )


dataclass = _dc.dataclass
globals()['dataclass'] = _dataclass

field = _field
