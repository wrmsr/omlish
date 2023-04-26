"""
TODO:
 - default_fn
  - toposort
 - type_check
 - kwonly
 - coerce
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
field = _dc.field

globals()['dataclass'] = _dataclass
globals()['field'] = _field
