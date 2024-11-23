# ruff: noqa: UP006 UP007
import typing as ta

from .ostypes import Pid
from .types import Process


##


class ProcessStateError(RuntimeError):
    pass


##


class PidHistory(ta.Dict[Pid, Process]):
    pass
