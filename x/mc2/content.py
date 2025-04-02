import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .typedvalues import ScalarTypedValue
from .typedvalues import TypedValue
from .typedvalues import TypedValueContainer
from .typedvalues import TypedValues


T = ta.TypeVar('T')

ContentDetailT = ta.TypeVar('ContentDetailT', bound='ContentDetail')
ContentT = ta.TypeVar('ContentT', bound='Content')


##


class ContentDetail(TypedValue, lang.Abstract):
    pass


class ScalarDetail(ScalarTypedValue[T], ContentDetail, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Content(TypedValueContainer[ContentDetailT], lang.Abstract):
    details: TypedValues[ContentDetailT] | None = dc.field(
        default=None,
        kw_only=True,
        metadata={
            dc.FieldExtras: dc.FieldExtras(
                repr_fn=lang.opt_repr,
                repr_priority=100,
            ),
        },
    )

    def with_details(self, *details: ContentDetailT) -> ta.Self:
        return dc.replace(self, outputs=TypedValues(
            *(self.details or []),
            *details,
        ))

    @property
    def _typed_values(self) -> TypedValues[ContentDetailT] | None:
        return self.details
