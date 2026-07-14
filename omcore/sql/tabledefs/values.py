# ruff: noqa: UP007
import typing as ta

from ... import dataclasses as dc
from ... import lang


##


@dc.dataclass(frozen=True)
class SpecialValue(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True)
class Now(SpecialValue, lang.Singleton):
    pass


##


SimpleValue: ta.TypeAlias = ta.Union[
    bool,
    int,
    float,
    str,

    SpecialValue,
]
