import operator
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import marshal as msh
from omlish import reflect as rfl
from omlish import typedvalues as tv
from omlish.funcs import match as mfs
from omlish.typedvalues.marshal import build_typed_values_marshaler
from omlish.typedvalues.marshal import build_typed_values_unmarshaler


##


@dc.dataclass()
class _TypedValuesFieldMarshalerFactory(msh.MarshalerFactoryMatchClass):
    tvs_rty: rfl.Type

    @mfs.simple(lambda _, ctx, rty: True)
    def _build(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        return build_typed_values_marshaler(ctx, self.tvs_rty)


@dc.dataclass()
class _TypedValuesFieldUnmarshalerFactory(msh.UnmarshalerFactoryMatchClass):
    tvs_rty: rfl.Type

    @mfs.simple(lambda _, ctx, rty: True)
    def _build(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        return build_typed_values_unmarshaler(ctx, self.tvs_rty)


##


def _tv_field_coercer(
        tvc: type[tv.TypedValue] | tuple[type[tv.TypedValue], ...],
) -> ta.Callable[[ta.Sequence], tv.TypedValues]:
    if isinstance(tvc, tuple):
        check.arg(all(issubclass(e, tv.TypedValue) for e in tvc))
    else:
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
        tvc: ta.Any,
        *,
        marshal_name: str | None = None,
) -> ta.Mapping:
    tvc_rty = rfl.type_(tvc)

    ct: ta.Any
    if isinstance(tvc_rty, type):
        ct = check.issubclass(tvc, tv.TypedValue)
    elif isinstance(tvc_rty, rfl.Union):
        ct = tuple(
            check.issubclass(check.not_none(rfl.get_concrete_type(a)), tv.TypedValue)  # noqa
            for a in tvc_rty.args
        )
    else:
        raise TypeError(tvc_rty)

    tvs_rty = rfl.type_(tv.TypedValues[tvc])

    return {
        **dc.extra_field_params(
            coerce=_tv_field_coercer(ct),
            repr_fn=_tv_field_repr,
        ),

        msh.FieldMetadata: msh.FieldMetadata(
            name=marshal_name,
            options=msh.FieldOptions(
                omit_if=operator.not_,
            ),
            marshaler_factory=_TypedValuesFieldMarshalerFactory(tvs_rty),
            unmarshaler_factory=_TypedValuesFieldUnmarshalerFactory(tvs_rty),
        ),
    }
