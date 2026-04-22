import typing as ta
import uuid

from omlish import lang
from omlish import typedvalues as tv

from ..metadata import CommonMetadata
from ..metadata import Metadata


##


class MessageMetadata(Metadata, lang.Abstract, lang.PackageSealed):
    pass


MessageMetadatas: ta.TypeAlias = MessageMetadata | CommonMetadata


##


class MessageUuid(tv.UniqueScalarTypedValue[uuid.UUID], MessageMetadata, lang.Final):
    pass


class TurnUuid(tv.UniqueScalarTypedValue[uuid.UUID], MessageMetadata, lang.Final):
    pass
