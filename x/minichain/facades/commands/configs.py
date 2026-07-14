import typing as ta

from omcore import dataclasses as dc


##


@dc.dataclass(frozen=True, kw_only=True)
class CommandsConfig:
    autoexec: ta.Sequence[str] | None = None
