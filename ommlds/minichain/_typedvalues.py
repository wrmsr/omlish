import operator
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl
from omlish import typedvalues as tv


if ta.TYPE_CHECKING:
    from . import _marshal
else:
    _marshal = lang.proxy_import('._marshal', __package__)


##


def _tv_field_coercer(
        tvc: type[tv.TypedValue] | tuple[type[tv.TypedValue], ...],
) -> ta.Callable[[ta.Sequence], tv.TypedValues]:
    if isinstance(tvc, tuple):
        check.arg(all(issubclass(e, tv.TypedValue) for e in tvc))

    else:
        check.issubclass(tvc, tv.TypedValue)

    def inner(seq):
        if isinstance(seq, tv.TypedValues):
            for e in seq:
                check.isinstance(e, tvc)
            return seq

        else:
            return tv.collect(*[
                check.isinstance(e, tvc)
                for e in check.isinstance(seq, ta.Sequence)
            ])

    return inner


def _tv_field_repr(tvs: tv.TypedValues) -> str | None:
    if not tvs:
        return None

    return repr(list(tvs))


def _tv_field_metadata(
        tvc: ta.Any,
        *,
        marshal_name: str | None = None,
) -> ta.Mapping:
    tvc_rty = rfl.reflect_type(tvc)

    ct: ta.Any
    if isinstance(tvc_rty, rfl.Instance):
        ct = check.issubclass(check.not_none(rfl.get_runtime_type_or_none(tvc_rty)), tv.TypedValue)
    elif isinstance(tvc_rty, rfl.UnionType):
        ct = tuple(
            check.issubclass(check.not_none(rfl.get_runtime_type_or_none(a)), tv.TypedValue)  # noqa
            for a in tvc_rty.items
        )
    else:
        raise TypeError(tvc_rty)

    tvs_rty = tv.TypedValues[tvc]  # noqa

    return {
        **dc.extra_field_params(
            coerce=_tv_field_coercer(ct),
            repr_fn=_tv_field_repr,
        ),

        msh.FieldOptions: msh.FieldOptions(
            name=marshal_name,

            omit_if=operator.not_,

            marshal_via=msh.MarshalVia(msh.FuncMarshalerFactory(
                lambda ctx, rty: _marshal._TypedValuesFieldMarshalerFactory(tvs_rty).make_marshaler(ctx, rty),  # noqa
            )),
            unmarshal_via=msh.UnmarshalVia(msh.FuncUnmarshalerFactory(
                lambda ctx, rty: _marshal._TypedValuesFieldUnmarshalerFactory(tvs_rty).make_unmarshaler(ctx, rty),  # noqa
            )),
        ),
    }
