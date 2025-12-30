from omlish import dataclasses as dc
from omlish import lang

from ..json import JsonValue
from .content import LeafContent
from .standard import StandardContent


##


@dc.dataclass(frozen=True)
class JsonContent(StandardContent, LeafContent, lang.Final):
    v: JsonValue
