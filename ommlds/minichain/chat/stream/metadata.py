import typing as ta
import uuid

from omlish import lang
from omlish import typedvalues as tv

from ..metadata import CommonMetadata
from ..metadata import Metadata


##


class AiDeltaMetadata(Metadata, lang.Abstract):
    pass


AiDeltaMetadatas: ta.TypeAlias = AiDeltaMetadata | CommonMetadata


##


class AiDeltaMessageUuid(tv.UniqueScalarTypedValue[uuid.UUID], AiDeltaMetadata, lang.Final):
    pass
