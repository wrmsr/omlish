import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..metadata import CommonMetadata
from ..metadata import Metadata
from .content import Content


##


class ContentMetadata(Metadata, lang.Abstract):
    pass


ContentMetadatas: ta.TypeAlias = ContentMetadata | CommonMetadata


##


@dc.dataclass(frozen=True)
class ContentOriginal(ContentMetadata, lang.Final):
    c: Content
