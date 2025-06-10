import typing as ta

from omlish import lang

from ..metadata import CommonMetadata
from ..metadata import Metadata


##


class ContentMetadata(Metadata, lang.Abstract):
    pass


ContentMetadatas: ta.TypeAlias = ContentMetadata | CommonMetadata
