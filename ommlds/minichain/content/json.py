from omlish import dataclasses as dc
from omlish import lang

from ..json import JsonValue
from .simple import SimpleSingleExtendedContent


##


@dc.dataclass(frozen=True)
class JsonContent(SimpleSingleExtendedContent, lang.Final):
    v: JsonValue
