import typing as ta

from omlish import lang

from ..metadata import CommonMetadata
from ..metadata import Metadata


##


class AiDeltaMetadata(Metadata, lang.Abstract):
    pass


AiDeltaMetadatas: ta.TypeAlias = AiDeltaMetadata | CommonMetadata
