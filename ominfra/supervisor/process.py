# ruff: noqa: UP006 UP007 UP045
import typing as ta

from .types import Process
from .utils.ostypes import Pid


##


class ProcessStateError(RuntimeError):
    pass


##


class PidHistory(ta.Dict[Pid, Process]):
    pass
