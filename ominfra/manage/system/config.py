# ruff: noqa: UP006 UP007
import dataclasses as dc
import typing as ta

from .platforms import Platform


@dc.dataclass(frozen=True)
class SystemConfig:
    platform: ta.Optional[Platform] = None
