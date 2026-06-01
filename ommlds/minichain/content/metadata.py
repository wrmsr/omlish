import contextvars
import typing as ta
import uuid

from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from ..metadata import CommonMetadata
from ..metadata import Metadata
from .content import Content


if ta.TYPE_CHECKING:
    from .standard import StandardContent


StandardContentT = ta.TypeVar('StandardContentT', bound='StandardContent')


##


class ContentMetadata(Metadata, lang.Abstract, lang.Sealed):
    pass


ContentMetadatas: ta.TypeAlias = ContentMetadata | CommonMetadata


##


class ContentUuid(tv.UniqueScalarTypedValue[uuid.UUID], ContentMetadata, lang.Final):
    pass


##


@dc.dataclass(frozen=True)
class ContentOriginal(ContentMetadata, lang.Final):
    c: Content


SUPPRESS_CONTENT_ORIGINALS_CV: contextvars.ContextVar[bool] = contextvars.ContextVar(
    f'{__name__}.SUPPRESS_CONTENT_ORIGINALS_CV',
    default=False,
)


def suppress_content_originals(st: bool = True) -> ta.ContextManager[None]:
    return SUPPRESS_CONTENT_ORIGINALS_CV.set(st)  # type: ignore[return-value]


def with_content_original(c: StandardContentT, *, original: Content) -> StandardContentT:
    if SUPPRESS_CONTENT_ORIGINALS_CV.get():
        return c

    return c._with_metadata(  # noqa
        ContentOriginal(original),
        discard=[ContentOriginal],
        mode='override',
    )
