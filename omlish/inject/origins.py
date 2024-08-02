import typing as ta

from .. import dataclasses as dc


@dc.dataclass(frozen=True)
class Origin:
    lst: ta.Sequence[str]


@dc.dataclass(frozen=True)
class Origins:
    lst: ta.Sequence[Origin]
