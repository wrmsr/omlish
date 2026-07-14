# ruff: noqa: UP007
import typing as ta

from omlish import lang

from ...metadata import CommonMetadata
from ...metadata import Metadata
from ..metadata import MessageUuid
from ..metadata import ThoughtSignature


##


class AiDeltaMetadata(Metadata, lang.Abstract, lang.Sealed):
    pass


AiDeltaMetadatas: ta.TypeAlias = ta.Union[
    AiDeltaMetadata,
    CommonMetadata,

    MessageUuid,
    ThoughtSignature,
]
