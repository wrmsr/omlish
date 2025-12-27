from omlish import dataclasses as dc
from omlish import lang

from ..json import JsonValue
from .standard import StandardContent
from .types import LeafContent


##


@dc.dataclass(frozen=True)
class JsonContent(StandardContent, LeafContent, lang.Final):
    v: JsonValue
