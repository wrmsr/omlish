import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from .._typedvalues import _tv_field_metadata
from ._typedvalues import _TypedValues


V_co = ta.TypeVar('V_co', covariant=True)


##


class RequestOption(tv.TypedValue, lang.Abstract):
    pass


# TODO: PEP696 default=RequestOption
RequestOptionT_co = ta.TypeVar('RequestOptionT_co', bound=RequestOption, covariant=True)


@dc.dataclass(frozen=True)
@dc.extra_class_params(
    allow_dynamic_dunder_attrs=True,
    terse_repr=True,
)
class Request(  # type: ignore[type-var]  # FIXME: _TypedValues param is invariant
    _TypedValues[RequestOptionT_co],
    lang.Final,
    ta.Generic[V_co, RequestOptionT_co],
):
    v: V_co

    _options: ta.Sequence[RequestOptionT_co] = dc.field(
        default=(),
        metadata=_tv_field_metadata(
            RequestOption,
            marshal_name='options',
        ),
    )

    @property
    def options(self) -> tv.TypedValues[RequestOptionT_co]:
        return check.isinstance(self._options, tv.TypedValues)

    @property
    def _typed_values(self) -> tv.TypedValues[RequestOptionT_co]:
        return check.isinstance(self._options, tv.TypedValues)

    def validate(self) -> ta.Self:
        self._check_typed_values()
        return self


RequestT_contra = ta.TypeVar('RequestT_contra', bound=Request, contravariant=True)
