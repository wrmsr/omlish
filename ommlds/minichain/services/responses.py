import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from .._typedvalues import _tv_field_metadata
from ._typedvalues import _TypedValues


V_co = ta.TypeVar('V_co', covariant=True)


##


class ResponseOutput(tv.TypedValue, lang.Abstract):
    pass


# TODO: PEP696 default=ResponseOutput
ResponseOutputT_contra = ta.TypeVar('ResponseOutputT_contra', bound=ResponseOutput, contravariant=True)


@dc.dataclass(frozen=True)
@dc.extra_class_params(
    allow_dynamic_dunder_attrs=True,
    terse_repr=True,
)
class Response(  # type: ignore[type-var]  # FIXME: _TypedValues param is invariant
    _TypedValues[ResponseOutputT_contra],
    lang.Final,
    ta.Generic[V_co, ResponseOutputT_contra],
):
    v: V_co

    _outputs: ta.Sequence[ResponseOutputT_contra] = dc.field(
        default=(),
        metadata=_tv_field_metadata(
            ResponseOutput,
            marshal_name='outputs',
        ),
    )

    @property
    def outputs(self) -> tv.TypedValues[ResponseOutputT_contra]:
        return check.isinstance(self._outputs, tv.TypedValues)

    @property
    def _typed_values(self) -> tv.TypedValues[ResponseOutputT_contra]:
        return check.isinstance(self._outputs, tv.TypedValues)

    def validate(self) -> ta.Self:
        self._check_typed_values()
        return self


ResponseT_co = ta.TypeVar('ResponseT_co', bound=Response, covariant=True)
