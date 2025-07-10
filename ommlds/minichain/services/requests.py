import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from .._typedvalues import _tv_field_metadata
from ..types import Option
from ..types import OptionT_co
from ._typedvalues import _TypedValues


V_co = ta.TypeVar('V_co', covariant=True)

OptionU = ta.TypeVar('OptionU', bound=Option)


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(
    allow_dynamic_dunder_attrs=True,
    terse_repr=True,
)
class Request(  # type: ignore[type-var]  # FIXME: _TypedValues param is invariant
    _TypedValues[OptionT_co],
    lang.Final,
    ta.Generic[V_co, OptionT_co],
):
    v: V_co  # type: ignore[misc]  # FIXME: Cannot use a covariant type variable as a parameter

    _options: ta.Sequence[OptionT_co] = dc.field(
        default=(),
        metadata=_tv_field_metadata(
            Option,
            marshal_name='options',
        ),
    )

    @property
    def options(self) -> tv.TypedValues[OptionT_co]:
        return check.isinstance(self._options, tv.TypedValues)

    def with_options(self, *options: OptionU, override: bool = False) -> 'Request[V_co, OptionT_co | OptionU]':
        return dc.replace(self, _options=self.options.update(*options, override=override))

    @property
    def _typed_values(self) -> tv.TypedValues[OptionT_co]:
        return check.isinstance(self._options, tv.TypedValues)

    def validate(self) -> ta.Self:
        self._check_typed_values()
        return self


RequestT_contra = ta.TypeVar('RequestT_contra', bound=Request, contravariant=True)
