import dataclasses as dc
import typing as ta


##


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
    line_type: str
