import typing as ta

from ..... import check
from ...._internals import StdParams
from ....specs import ClassSpec
from ....specs import FieldSpec


##


def std_params_to_class_spec(
        p: StdParams,
        fields: ta.Sequence[FieldSpec],
        *,
        metadata: ta.Sequence[ta.Any] | None = None,
) -> ClassSpec:
    return ClassSpec(
        fields=fields,

        init=check.isinstance(p.init, bool),
        repr=check.isinstance(p.repr, bool),
        eq=check.isinstance(p.eq, bool),
        order=check.isinstance(p.order, bool),
        unsafe_hash=check.isinstance(p.unsafe_hash, bool),
        frozen=check.isinstance(p.frozen, bool),

        match_args=check.isinstance(p.match_args, bool),
        kw_only=check.isinstance(p.kw_only, bool),
        slots=check.isinstance(p.slots, bool),
        weakref_slot=check.isinstance(p.weakref_slot, bool),

        metadata=metadata,
    )
