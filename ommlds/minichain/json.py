import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


@dc.dataclass(frozen=True)
class JsonSchema(lang.Final):
    name: str
    root: ta.Any
