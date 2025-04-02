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
    details: TypedValues[ContentDetailT] | None = dc.field(default=None, kw_only=True)

    @property
    def _typed_values(self) -> TypedValues[ContentDetailT] | None:
        return self.details
