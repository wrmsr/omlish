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
from ._typedvalues import _TypedValues


V_co = ta.TypeVar('V_co', covariant=True)


##


class ResponseMetadata(Metadata, lang.Abstract):
    pass


ResponseMetadatas: ta.TypeAlias = ResponseMetadata | CommonMetadata


##


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
    v: V_co  # type: ignore[misc]  # FIXME: Cannot use a covariant type variable as a parameter

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

        return dc.replace(self, _outputs=new)

    @property
    def _typed_values(self) -> tv.TypedValues[OutputT_contra]:
        return check.isinstance(self._outputs, tv.TypedValues)

    def validate(self) -> ta.Self:
        self._check_typed_values()
        return self

    _metadata: ta.Sequence[ResponseMetadatas] = dc.field(
        default=(),
        kw_only=True,
        repr=False,
    )

    MetadataContainerDataclass._configure_metadata_field(_metadata, ResponseMetadatas)  # noqa


ResponseT_co = ta.TypeVar('ResponseT_co', bound=Response, covariant=True)
