import typing as ta

from omlish import lang

from ...metadata import CommonMetadata
from ...metadata import Metadata
from ..metadata import MessageUuid


##


class AiDeltaMetadata(Metadata, lang.Abstract, lang.Sealed):
    pass


AiDeltaMetadatas: ta.TypeAlias = AiDeltaMetadata | CommonMetadata | MessageUuid
