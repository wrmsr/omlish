import dataclasses as dc
import typing as ta

from omlish import lang


##


@dc.dataclass(frozen=True)
class JsonSchema(lang.Final):
    name: str
    root: ta.Any
