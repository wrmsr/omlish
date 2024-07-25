import dataclasses as dc

from omlish import lang


##


class ServerEvent(lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class RawData(ServerEvent):
    data: bytes
    address: tuple[str, int] | None = None


@dc.dataclass(frozen=True)
class Closed(ServerEvent):
    pass


@dc.dataclass(frozen=True)
class Updated(ServerEvent):
    idle: bool


##


@dc.dataclass(frozen=True)
class ProtocolEvent:
    stream_id: int


@dc.dataclass(frozen=True)
class Request(ProtocolEvent):
    headers: list[tuple[bytes, bytes]]
    http_version: str
    method: str
    raw_path: bytes


@dc.dataclass(frozen=True)
class Body(ProtocolEvent):
    data: bytes


@dc.dataclass(frozen=True)
class EndBody(ProtocolEvent):
    pass


@dc.dataclass(frozen=True)
class Data(ProtocolEvent):
    data: bytes


@dc.dataclass(frozen=True)
class EndData(ProtocolEvent):
    pass


@dc.dataclass(frozen=True)
class Response(ProtocolEvent):
    headers: list[tuple[bytes, bytes]]
    status_code: int


@dc.dataclass(frozen=True)
class InformationalResponse(ProtocolEvent):
    headers: list[tuple[bytes, bytes]]
    status_code: int

    def __post_init__(self) -> None:
        if self.status_code >= 200 or self.status_code < 100:
            raise ValueError(f'Status code must be 1XX not {self.status_code}')


@dc.dataclass(frozen=True)
class StreamClosed(ProtocolEvent):
    pass
