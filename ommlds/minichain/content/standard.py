import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..metadata import MetadataContainerDataclass
from .content import BaseContent
from .metadata import ContentMetadatas
from .metadata import with_content_original


##


@dc.dataclass(frozen=True)
class StandardContent(  # noqa
    MetadataContainerDataclass[ContentMetadatas],
    BaseContent,
    lang.Abstract,
):
    _metadata: ta.Sequence[ContentMetadatas] = dc.field(
        default=(),
        kw_only=True,
        repr=False,
    )

    MetadataContainerDataclass._configure_metadata_field(_metadata, ContentMetadatas)  # noqa

    def replace(self, **kwargs: ta.Any) -> ta.Self:
        if (n := dc.replace_is_not(self, **kwargs)) is self:
            return self
        return with_content_original(n, original=self)
