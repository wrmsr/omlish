"""
https://www.jsonrpc.org/specification
"""
import operator
import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish.formats import json


Number: ta.TypeAlias = int | float
Object: ta.TypeAlias = ta.Mapping[str, ta.Any]
Id: ta.TypeAlias = str | Number | None


##


VERSION = '2.0'


class NotSpecified(lang.Marker):
    pass


def is_not_specified(v: ta.Any) -> bool:
    return v is NotSpecified


##


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['id'], omit_if=is_not_specified)
@msh.update_fields_metadata(['params'], omit_if=operator.not_)
class Request:
    id: Id | type[NotSpecified]
    method: str
    params: Object | None = None

    jsonrpc: str = dc.field(default=VERSION, kw_only=True)
    dc.validate(lambda self: self.jsonrpc == VERSION)


##


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['result', 'error'], omit_if=is_not_specified)
class Response:
    id: Id

    result: ta.Any = NotSpecified
    error: ta.Union['Error', type[NotSpecified]] = NotSpecified
    dc.validate(lambda self: is_not_specified(self.result) ^ is_not_specified(self.error))

    jsonrpc: str = dc.field(default=VERSION, kw_only=True)
    dc.validate(lambda self: self.jsonrpc == VERSION)


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['data'], omit_if=is_not_specified)
class Error:
    code: int
    message: str
    data: ta.Any = NotSpecified


#


@dc.dataclass(frozen=True)
class KnownError:
    code: int
    message: str
    meaning: str


class KnownErrors(lang.Namespace):
    PARSE_ERROR = KnownError(-32700, 'Parse error', 'Invalid JSON was received by the server.')
    INVALID_REQUEST = KnownError(-32600, 'Invalid Request', 'The JSON sent is not a valid Request object.')
    METHOD_NOT_FOUND = KnownError(-32601, 'Method not found', 'The method does not exist / is not available.')
    INVALID_PARAMS = KnownError(-32602, 'Invalid params', 'Invalid method parameter(s).')
    INTERNAL_ERROR = KnownError(-32603, 'Internal error', 'Internal JSON-RPC error.')


CUSTOM_ERROR_BASE = -32000


##


def _main() -> None:
    pass


if __name__ == '__main__':
    _main()
