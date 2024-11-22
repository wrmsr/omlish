# ruff: noqa: UP006 UP007
import typing as ta

from .types import Process


##


class ProcessStateError(RuntimeError):
    pass


##


class PidHistory(ta.Dict[int, Process]):
    pass
