import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv


T = ta.TypeVar('T')

ContentDetailT = ta.TypeVar('ContentDetailT', bound='ContentDetail')
ContentT = ta.TypeVar('ContentT', bound='Content')


##


class ContentDetail(tv.TypedValue, lang.Abstract):
    pass


class ScalarDetail(tv.ScalarTypedValue[T], ContentDetail, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Content(tv.TypedValueHolder[ContentDetailT], lang.Abstract):
    details: tv.TypedValues[ContentDetailT] | None = dc.field(
        default=None,
        kw_only=True,
        metadata={
            dc.FieldExtras: dc.FieldExtras(
                repr_fn=lang.opt_repr,
                repr_priority=100,
            ),
        },
    )

    def with_details(self: ContentT, *details: ContentDetailT) -> ContentT:
        return dc.replace(self, outputs=tv.TypedValues(
            *(self.details or []),
            *details,
        ))

    @property
    def _typed_values(self) -> tv.TypedValues[ContentDetailT] | None:
        return self.details
