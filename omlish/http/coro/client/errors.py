# @omlish-lite
# ruff: noqa: UP006 UP007 UP043 UP045
import dataclasses as dc
import enum
import typing as ta


##


class CoroHttpClientErrors:
    class ClientError(Exception):
        pass

    class NotConnectedError(ClientError):
        pass

    class InvalidUrlError(ClientError):
        pass

    @dc.dataclass()
    class UnknownProtocolError(ClientError):
        version: str

    @dc.dataclass()
    class IncompleteReadError(ClientError):
        partial: bytes
        expected: ta.Optional[int] = None

    class ImproperConnectionStateError(ClientError):
        pass

    class CannotSendRequestError(ImproperConnectionStateError):
        pass

    class CannotSendHeaderError(ImproperConnectionStateError):
        pass

    class ResponseNotReadyError(ImproperConnectionStateError):
        pass

    @dc.dataclass()
    class BadStatusLineError(ClientError):
        line: str

    class RemoteDisconnectedError(BadStatusLineError, ConnectionResetError):
        pass

    @dc.dataclass()
    class LineTooLongError(ClientError):
        class LineType(enum.Enum):
            STATUS = enum.auto()
            HEADER = enum.auto()
            CHUNK_SIZE = enum.auto()
            TRAILER = enum.auto()

        line_type: LineType
