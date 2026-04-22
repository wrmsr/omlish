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


def with_content_original(c: StandardContentT, *, original: Content) -> StandardContentT:
    return c._with_metadata(  # noqa
        ContentOriginal(original),
        discard=[ContentOriginal],
        override=True,
    )
