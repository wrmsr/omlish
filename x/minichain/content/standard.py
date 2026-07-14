import typing as ta

from omcore import dataclasses as dc
from omcore import lang

from ..metadata import MetadataContainerDataclass
from .content import ContentBase
from .metadata import ContentMetadatas


##


@dc.dataclass(frozen=True)
class StandardContent(MetadataContainerDataclass[ContentMetadatas], ContentBase, lang.Abstract):
    _metadata: ta.Sequence[ContentMetadatas] = dc.field(default=(), kw_only=True, repr=False)

    MetadataContainerDataclass._configure_metadata_field(_metadata, ContentMetadatas)  # noqa
