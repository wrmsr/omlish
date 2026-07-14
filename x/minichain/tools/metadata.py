import typing as ta
import uuid

from omcore import lang
from omcore import marshal as msh
from omcore import typedvalues as tv

from ..metadata import CommonMetadata
from ..metadata import Metadata


##


@msh.set_polymorphic_from_subclasses(naming=msh.Naming.SNAKE)
class ToolUseMetadata(Metadata, lang.Abstract, lang.Sealed):
    pass


ToolUseMetadatas: ta.TypeAlias = ToolUseMetadata | CommonMetadata


##


class ToolUseUuid(tv.UniqueScalarTypedValue[uuid.UUID], ToolUseMetadata, lang.Final):
    pass


##


@msh.set_polymorphic_from_subclasses(naming=msh.Naming.SNAKE)
class ToolUseResultMetadata(Metadata, lang.Abstract, lang.Sealed):
    pass


ToolUseResultMetadatas: ta.TypeAlias = ToolUseResultMetadata | CommonMetadata
