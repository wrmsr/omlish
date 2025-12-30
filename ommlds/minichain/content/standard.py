import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from .._typedvalues import _tv_field_metadata
from ..metadata import MetadataContainer
from .content import BaseContent
from .metadata import ContentMetadatas
from .metadata import ContentOriginal


##


@dc.dataclass(frozen=True)
class StandardContent(  # noqa
    MetadataContainer[ContentMetadatas],
    BaseContent,
    lang.Abstract,
):
    _metadata: ta.Sequence[ContentMetadatas] = dc.field(
        default=(),
        kw_only=True,
        repr=False,
        metadata=_tv_field_metadata(
            ContentMetadatas,
            marshal_name='metadata',
        ),
    )

    @property
    def metadata(self) -> tv.TypedValues[ContentMetadatas]:
        return check.isinstance(self._metadata, tv.TypedValues)

    def with_metadata(self, *mds: ContentMetadatas, override: bool = False) -> ta.Self:
        nmd = (md := self.metadata).update(*mds, override=override)
        if nmd is md:
            return self
        return dc.replace(self, _metadata=nmd)

    def replace(self, **kwargs: ta.Any) -> ta.Self:
        if (n := dc.replace_is_not(self, **kwargs)) is self:
            return self
        return n.with_metadata(ContentOriginal(self), override=True)
