import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from .._typedvalues import _tv_field_metadata
from ..metadata import CommonMetadata
from ..metadata import Metadata
from ..metadata import MetadataContainerDataclass
from ..types import Output
from ..types import OutputT_contra
from ._origclasses import confer_orig_class
from ._typedvalues import _TypedValues


V_co = ta.TypeVar('V_co', covariant=True)


##


class ResponseMetadata(Metadata, lang.Abstract):
    pass


ResponseMetadatas: ta.TypeAlias = ResponseMetadata | CommonMetadata


##


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(
    allow_dynamic_dunder_attrs=True,
    terse_repr=True,
)
class Response(  # type: ignore[type-var]  # FIXME: _TypedValues param is invariant
    _TypedValues[OutputT_contra],
    MetadataContainerDataclass[ResponseMetadatas],
    lang.Final,
    ta.Generic[V_co, OutputT_contra],
):
    """
    Universal service response, comprised of:
     - a value of type `V_co`
     - a sequence of outputs of type `OutputT_contra`
     - metadata of type `ResponseMetadatas`

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

    _outputs: ta.Sequence[OutputT_contra] = dc.field(
        default=(),
        metadata=_tv_field_metadata(
            Output,
            marshal_name='outputs',
        ),
    )

    @property
    def outputs(self) -> tv.TypedValues[OutputT_contra]:
        return check.isinstance(self._outputs, tv.TypedValues)

    @property
    def _typed_values(self) -> tv.TypedValues[OutputT_contra]:
        return check.isinstance(self._outputs, tv.TypedValues)

    def with_outputs(
            self,
            *add: OutputT_contra,
            discard: ta.Iterable[type] | None = None,
            override: bool = False,
    ) -> ta.Self:
        new = (old := self.outputs).update(
            *add,
            discard=discard,
            override=override,
        )

        if new is old:
            return self

        return confer_orig_class(self, dc.replace(self, _outputs=new))

    #

    _metadata: ta.Sequence[ResponseMetadatas] = dc.field(
        default=(),
        kw_only=True,
        repr=False,
    )

    MetadataContainerDataclass._configure_metadata_field(_metadata, ResponseMetadatas)  # noqa

    def with_metadata(
            self,
            *add: ResponseMetadatas,
            discard: ta.Iterable[type] | None = None,
            override: bool = False,
    ) -> ta.Self:
        return confer_orig_class(self, super().with_metadata(*add, discard=discard, override=override))

    #

    def validate(self) -> ta.Self:
        self._check_typed_values()
        return self


ResponseT_co = ta.TypeVar('ResponseT_co', bound=Response, covariant=True)
