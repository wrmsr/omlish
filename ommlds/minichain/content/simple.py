import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from .._typedvalues import _tv_field_metadata
from ..metadata import MetadataContainer
from .metadata import ContentMetadatas
from .types import ExtendedContent
from .types import SingleExtendedContent


##


@dc.dataclass(frozen=True)
class SimpleExtendedContent(  # noqa
    MetadataContainer[ContentMetadatas],
    ExtendedContent,
    lang.Abstract,
):
    _metadata: ta.Sequence[ContentMetadatas] = dc.field(
        default=(),
        kw_only=True,
        metadata=_tv_field_metadata(
            ContentMetadatas,
            marshal_name='metadata',
        ),
    )

    @property
    def metadata(self) -> tv.TypedValues[ContentMetadatas]:
        return check.isinstance(self._metadata, tv.TypedValues)

    def with_metadata(self, *mds: ContentMetadatas, override: bool = False) -> ta.Self:
        return dc.replace(self, _metadata=tv.TypedValues(*self._metadata, *mds, override=override))


@dc.dataclass(frozen=True)
class SimpleSingleExtendedContent(
    SimpleExtendedContent,
    SingleExtendedContent,
    lang.Abstract,
):
    pass
