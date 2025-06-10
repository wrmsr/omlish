import operator
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import marshal as msh
from omlish import typedvalues as tv


##


def _tv_field_coercer(tvc: type[tv.TypedValue]) -> ta.Callable[[ta.Sequence], tv.TypedValues]:
    check.issubclass(tvc, tv.TypedValue)

    def inner(seq):
        return tv.TypedValues(*[
            check.isinstance(e, tvc)
            for e in check.isinstance(seq, ta.Sequence)
        ])

    return inner


def _tv_field_repr(tvs: tv.TypedValues) -> str | None:
    if not tvs:
        return None

    return repr(list(tvs))


def _tv_field_metadata(
        tvc: type[tv.TypedValue],
        *,
        marshal_name: str | None = None,
) -> ta.Mapping:
    check.issubclass(tvc, tv.TypedValue)

    return {
        **dc.extra_field_params(
            coerce=_tv_field_coercer(tvc),
            repr_fn=_tv_field_repr,
        ),

        msh.FieldMetadata: msh.FieldMetadata(
            name=marshal_name,
            options=msh.FieldOptions(
                omit_if=operator.not_,
            ),
        ),
    }
