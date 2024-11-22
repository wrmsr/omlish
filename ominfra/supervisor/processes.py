import typing as ta

from .types import Process


##


class ProcessStateError(RuntimeError):
    pass


##


class PidHistory(ta.Dict[int, Process]):
    pass
