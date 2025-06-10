import typing as ta

from omlish import lang

from ..metadata import CommonMetadata
from ..metadata import Metadata


##


class MessageMetadata(Metadata, lang.Abstract):
    pass


MessageMetadatas: ta.TypeAlias = MessageMetadata | CommonMetadata
