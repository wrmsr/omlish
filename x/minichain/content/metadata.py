import typing as ta
import uuid

from omcore import lang
from omcore import typedvalues as tv

from ..metadata import CommonMetadata
from ..metadata import Metadata


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
