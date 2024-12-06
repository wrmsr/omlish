# ruff: noqa: UP006 UP007
import dataclasses as dc
import typing as ta


@dc.dataclass(frozen=True)
class MainConfig:
    log_level: ta.Optional[str] = 'INFO'

    debug: bool = False
