# @omlish-lite
# ruff: noqa: UP006 UP007 UP043 UP045
import abc
import dataclasses as dc
import typing as ta


##


class CoroHttpClientIo:
    MAX_LINE: ta.ClassVar[int] = 65536

    #

    class Io(abc.ABC):  # noqa
        pass

    #

    @dc.dataclass(frozen=True)
    class ConnectIo(Io):
        args: ta.Tuple[ta.Any, ...]
        kwargs: ta.Optional[ta.Dict[str, ta.Any]] = None

    class CloseIo(Io):
        pass

    #

    class AnyReadIo(Io):  # noqa
        pass

    @dc.dataclass(frozen=True)
    class ReadIo(AnyReadIo):
        sz: ta.Optional[int]

    @dc.dataclass(frozen=True)
    class ReadLineIo(AnyReadIo):
        sz: int

    @dc.dataclass(frozen=True)
    class PeekIo(AnyReadIo):
        sz: int

    #

    @dc.dataclass(frozen=True)
    class WriteIo(Io):
        data: bytes
