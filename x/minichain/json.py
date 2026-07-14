# ruff: noqa: UP007
import typing as ta

from omcore import dataclasses as dc
from omcore import lang


##


@dc.dataclass(frozen=True)
class JsonSchema(lang.Final):
    name: str
    root: ta.Any


##


JsonValue: ta.TypeAlias = ta.Union[
    ta.Mapping[str, 'JsonValue'],

    ta.Sequence['JsonValue'],

    str,

    int,
    float,

    bool,

    None,
]
