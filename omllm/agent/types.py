import typing as ta

from omcore import dataclasses as dc


##


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
class Context:
    pass
