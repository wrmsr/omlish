# ruff: noqa: UP006 UP007
import dataclasses as dc
import typing as ta


@dc.dataclass(frozen=True)
class SystemConfig:
    platform: ta.Optional[str] = None
