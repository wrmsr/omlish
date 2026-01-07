import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from .._typedvalues import _tv_field_metadata
from ..metadata import CommonMetadata
from ..metadata import Metadata
from ..metadata import MetadataContainerDataclass
from ..types import Option
from ..types import OptionT_co
from ._origclasses import confer_orig_class
from ._typedvalues import _TypedValues


V_co = ta.TypeVar('V_co', covariant=True)

OptionU = ta.TypeVar('OptionU', bound=Option)


##


class RequestMetadata(Metadata, lang.Abstract):
    pass


RequestMetadatas: ta.TypeAlias = RequestMetadata | CommonMetadata


##


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(
    allow_dynamic_dunder_attrs=True,
    terse_repr=True,
)
class Request(  # type: ignore[type-var]  # FIXME: _TypedValues param is invariant
    _TypedValues[OptionT_co],
    MetadataContainerDataclass[RequestMetadatas],
    lang.Final,
    ta.Generic[V_co, OptionT_co],
):
    """
    Universal service request, comprised of:
     - a value of type `V_co`
     - a sequence of options of type `OptionT_co`
     - metadata of type `RequestMetadatas`

    Refer to the package README.md for an explanation of its type var variance.

    This class is final, but each instance's `__orig_class__` (if present) is significant. It is encouraged to construct
    these through a pre-parameterized type alias, and the provided `with_` methods should be used rather than
    `dc.replace` (as they will propagate `__orig_class__`).
    """

    #

    v: V_co  # type: ignore[misc]  # FIXME: Cannot use a covariant type variable as a parameter

    def with_v(self, v: V_co) -> ta.Self:  # type: ignore[misc]
        return confer_orig_class(self, dc.replace(self, v=v))

    #

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

    @property
    def _typed_values(self) -> tv.TypedValues[OptionT_co]:
        return check.isinstance(self._options, tv.TypedValues)

    def with_options(
            self,
            *add: OptionU,
            discard: ta.Iterable[type] | None = None,
            override: bool = False,
    ) -> 'Request[V_co, OptionT_co | OptionU]':
        new = (old := self.options).update(
            *add,
            discard=discard,
            override=override,
        )

        if new is old:
            return self

        return confer_orig_class(self, dc.replace(self, _options=new))

    #

    _metadata: ta.Sequence[RequestMetadatas] = dc.field(
        default=(),
        kw_only=True,
        repr=False,
    )

    MetadataContainerDataclass._configure_metadata_field(_metadata, RequestMetadatas)  # noqa

    def with_metadata(
            self,
            *add: RequestMetadatas,
            discard: ta.Iterable[type] | None = None,
            override: bool = False,
    ) -> ta.Self:
        return confer_orig_class(self, super().with_metadata(*add, discard=discard, override=override))

    #

    def validate(self) -> ta.Self:
        self._check_typed_values()
        return self


RequestT_contra = ta.TypeVar('RequestT_contra', bound=Request, contravariant=True)
