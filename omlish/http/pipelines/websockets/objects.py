# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import enum
import typing as ta

from ....lite.abstract import Abstract
from ....lite.check import check


##


@ta.final
class IoPipelineWebsocketOpcode(enum.IntEnum):
    CONTINUATION = 0x0
    TEXT = 0x1
    BINARY = 0x2
    # 0x3 - 0x7 reserved non-control
    CLOSE = 0x8
    PING = 0x9
    PONG = 0xA
    # 0xB - 0xF reserved control


@ta.final
@dc.dataclass(frozen=True)
class IoPipelineWebsocketFrame:
    """A single websocket frame, payload is unmasked."""

    fin: bool
    opcode: IoPipelineWebsocketOpcode

    payload: bytes

    rsv1: bool = False
    rsv2: bool = False
    rsv3: bool = False

    def __post_init__(self) -> None:
        # Control frames must be <= 125 and not fragmented
        if self.opcode in (
            IoPipelineWebsocketOpcode.CLOSE,
            IoPipelineWebsocketOpcode.PING,
            IoPipelineWebsocketOpcode.PONG,
        ):
            check.arg(self.fin)
            check.arg(len(self.payload) <= 125)


##


class IoPipelineWebsocketObject(Abstract):
    pass


@ta.final
@dc.dataclass(frozen=True)
class IoPipelineWebsocketText(IoPipelineWebsocketObject):
    text: str


@ta.final
@dc.dataclass(frozen=True)
class IoPipelineWebsocketBinary(IoPipelineWebsocketObject):
    data: bytes


@ta.final
@dc.dataclass(frozen=True)
class IoPipelineWebsocketPing(IoPipelineWebsocketObject):
    data: bytes = b''

    def __post_init__(self) -> None:
        check.arg(len(self.data) <= 125)


@ta.final
@dc.dataclass(frozen=True)
class IoPipelineWebsocketPong(IoPipelineWebsocketObject):
    data: bytes = b''

    def __post_init__(self) -> None:
        check.arg(len(self.data) <= 125)


@ta.final
@dc.dataclass(frozen=True)
class IoPipelineWebsocketClose(IoPipelineWebsocketObject):
    code: int = 1000
    reason: str = ''

    def __post_init__(self) -> None:
        check.arg(0 <= self.code <= 0xFFFF)


@ta.final
@dc.dataclass(frozen=True)
class IoPipelineWebsocketOpen(IoPipelineWebsocketObject):
    subprotocol: ta.Optional[str] = None
    extensions: ta.Sequence[str] = ()


@ta.final
@dc.dataclass(frozen=True)
class IoPipelineWebsocketError(IoPipelineWebsocketObject):
    exc: BaseException
