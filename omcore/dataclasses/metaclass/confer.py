import dataclasses as dc
import typing as ta

from ..impl.api.classes.params import get_class_spec
from .specs import get_metaclass_spec


##


CONFER_CLASS_PARAMS: tuple[str, ...] = (
    'eq',
    'frozen',
    'kw_only',

    'reorder',
    'cache_hash',
    'generic_init',
    'override',

    'repr_id',
    'terse_repr',

    'allow_redundant_decorator',
)

CONFER_METACLASS_PARAMS: tuple[str, ...] = (
    'confer',
    'final_subclasses',
    'abstract_immediate_subclasses',
)


def confer_kwarg(out: dict[str, ta.Any], k: str, v: ta.Any) -> None:
    if k in out:
        if out[k] != v:
            raise ValueError
    else:
        out[k] = v


def confer_kwargs(
        bases: ta.Sequence[type],
        kwargs: ta.Mapping[str, ta.Any],
) -> dict[str, ta.Any]:
    out: dict[str, ta.Any] = {}
    for base in bases:
        if not dc.is_dataclass(base):
            continue

        if (bcs := get_class_spec(base)) is None:
            continue

        if not (bmp := get_metaclass_spec(bcs)).confer:
            continue

        for ck in bmp.confer:
            if ck in kwargs:
                continue

            if ck in CONFER_CLASS_PARAMS:
                confer_kwarg(out, ck, getattr(bcs, ck))

            elif ck in CONFER_METACLASS_PARAMS:
                confer_kwarg(out, ck, getattr(bmp, ck))

            else:
                raise KeyError(ck)

    return out
