import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..metadata import MetadataContainerDataclass
from .content import ContentBase
from .metadata import ContentMetadatas
from .metadata import with_content_original


##


@dc.dataclass(frozen=True)
class StandardContent(MetadataContainerDataclass[ContentMetadatas], ContentBase, lang.Abstract):
    _metadata: ta.Sequence[ContentMetadatas] = dc.field(default=(), kw_only=True, repr=False)

    MetadataContainerDataclass._configure_metadata_field(_metadata, ContentMetadatas)  # noqa

    def with_metadata(
            self,
            *add: ContentMetadatas,
            discard: ta.Literal['all'] | ta.Iterable[type] | None = None,
            mode: ta.Literal['append', 'prepend', 'override', 'default'] = 'append',
            no_original: bool = False,
    ) -> ta.Self:
        return self._with_metadata(
            *add,
            discard=discard,
            mode=mode,
            _replace=type(self).replace if not no_original else None,
        )

    #

    def replace(self, **kwargs: ta.Any) -> ta.Self:
        if (n := dc.replace_is_not(self, **kwargs)) is self:
            return self
        return with_content_original(n, original=self)
