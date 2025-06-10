import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from .._typedvalues import _tv_field_metadata
from .content import Content
from .content import ExtendedContent
from .metadata import ContentMetadata
from .metadata import MetadataContent


##


@dc.dataclass(frozen=True)
class ListContent(
    MetadataContent,
    ExtendedContent,
    lang.Final,
):
    l: ta.Sequence[Content]

    _metadata: ta.Sequence[ContentMetadata] = dc.field(
        default=(),
        metadata=_tv_field_metadata(
            ContentMetadata,
            marshal_name='metadata',
        ),
    )

    @property
    def metadata(self) -> tv.TypedValues[ContentMetadata]:
        return check.isinstance(self._metadata, tv.TypedValues)
