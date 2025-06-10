"""
TODO:
  - lazy load
  - serialize fs path not data
"""
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from .._typedvalues import _tv_field_metadata
from ..metadata import MetadataContainer
from .content import ExtendedContent
from .metadata import ContentMetadatas


if ta.TYPE_CHECKING:
    import PIL.Image as pimg  # noqa
else:
    pimg = lang.proxy_import('PIL.Image')


##


@dc.dataclass(frozen=True)
class ImageContent(
    MetadataContainer[ContentMetadatas],
    ExtendedContent,
    lang.Final,
):
    i: 'pimg.Image' = dc.field()

    _metadata: ta.Sequence[ContentMetadatas] = dc.field(
        default=(),
        metadata=_tv_field_metadata(
            ContentMetadatas,
            marshal_name='metadata',
        ),
    )

    @property
    def metadata(self) -> tv.TypedValues[ContentMetadatas]:
        return check.isinstance(self._metadata, tv.TypedValues)
