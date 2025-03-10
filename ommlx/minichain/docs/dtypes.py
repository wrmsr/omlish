import enum

from omlish import dataclasses as dc
from omlish import lang

from ..vectors.vectors import Vector


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
