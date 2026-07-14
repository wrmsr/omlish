import enum

from omcore import dataclasses as dc
from omcore import lang

from ..vectors.types import Vector


##


@dc.dataclass(frozen=True)
class Dtype(lang.Final):
    name: str
    cls: type

    _: dc.KW_ONLY

    primitive: bool = False


class Dtypes(enum.Enum):
    STR = Dtype('str', str, primitive=True)
    BYTES = Dtype('bytes', bytes, primitive=True)

    INT = Dtype('int', int, primitive=True)
    FLOAT = Dtype('float', float, primitive=True)

    VECTOR = Dtype('vector', Vector)
