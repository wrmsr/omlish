from omlish import dataclasses as dc
from omlish import lang

from ..json import JsonValue
from .standard import StandardContent


##


@dc.dataclass(frozen=True)
class JsonContent(StandardContent, lang.Final):
    v: JsonValue
