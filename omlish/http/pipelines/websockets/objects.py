# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import enum
import typing as ta

from ....lite.abstract import Abstract
from ....lite.check import check


##


class IoPipelineWebsocketObject(Abstract):
    """Marker base for websocket pipeline objects."""


@ta.final
class WsOpcode(enum.IntEnum):
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
class WsFrame(IoPipelineWebsocketObject):
    """A single websocket frame, payload is unmasked."""

    fin: bool
    opcode: WsOpcode

    payload: bytes

    rsv1: bool = False
    rsv2: bool = False
    rsv3: bool = False

    def __post_init__(self) -> None:
        # Control frames must be <= 125 and not fragmented
        if self.opcode in (WsOpcode.CLOSE, WsOpcode.PING, WsOpcode.PONG):
            check.arg(self.fin)
            check.arg(len(self.payload) <= 125)


@ta.final
@dc.dataclass(frozen=True)
class WsText(IoPipelineWebsocketObject):
    text: str


@ta.final
@dc.dataclass(frozen=True)
class WsBinary(IoPipelineWebsocketObject):
    data: bytes


@ta.final
@dc.dataclass(frozen=True)
class WsPing(IoPipelineWebsocketObject):
    data: bytes = b''

    def __post_init__(self) -> None:
        check.arg(len(self.data) <= 125)


@ta.final
@dc.dataclass(frozen=True)
class WsPong(IoPipelineWebsocketObject):
    data: bytes = b''

    def __post_init__(self) -> None:
        check.arg(len(self.data) <= 125)


@ta.final
@dc.dataclass(frozen=True)
class WsClose(IoPipelineWebsocketObject):
    code: int = 1000
    reason: str = ''

    def __post_init__(self) -> None:
        check.arg(0 <= self.code <= 0xFFFF)


@ta.final
@dc.dataclass(frozen=True)
class WsOpen(IoPipelineWebsocketObject):
    subprotocol: ta.Optional[str] = None
    extensions: ta.Sequence[str] = ()


@ta.final
@dc.dataclass(frozen=True)
class WsError(IoPipelineWebsocketObject):
    exc: BaseException
