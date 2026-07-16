import typing as ta

from omcore import dataclasses as dc


##


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
class State:
    pass


class Agent:
    def __init__(
            self,
    ) -> None:
        super().__init__()
