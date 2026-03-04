import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..metadata import CommonMetadata
from ..metadata import Metadata
from .content import Content


if ta.TYPE_CHECKING:
    from .standard import StandardContent


StandardContentT = ta.TypeVar('StandardContentT', bound='StandardContent')


##


class ContentMetadata(Metadata, lang.Abstract):
    pass


ContentMetadatas: ta.TypeAlias = ContentMetadata | CommonMetadata


##


@dc.dataclass(frozen=True)
class ContentOriginal(ContentMetadata, lang.Final):
    c: Content


def with_content_original(c: StandardContentT, *, original: Content) -> StandardContentT:
    return c.with_metadata(ContentOriginal(original), discard=[ContentOriginal], override=True)
