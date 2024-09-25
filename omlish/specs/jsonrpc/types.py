"""
https://www.jsonrpc.org/specification

TODO:
 - drop NotSpecified, use lang.Maybe, make marshal do that
 - server/client impl

See:
 - https://github.com/python-lsp/python-lsp-jsonrpc
"""
import operator
import typing as ta

from ... import dataclasses as dc
from ... import lang
from ... import marshal as msh


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
@msh.update_fields_metadata(['id'], omit_if=is_not_specified, default=lang.just(NotSpecified))
@msh.update_fields_metadata(['params'], omit_if=operator.not_)
class Request(lang.Final):
    id: Id | type[NotSpecified]
    method: str
    params: Object | None = None

    jsonrpc: str = dc.field(default=VERSION, kw_only=True)
    dc.validate(lambda self: self.jsonrpc == VERSION)


def request(id: Id, method: str, params: Object | None = None) -> Request:  # noqa
    return Request(id, method, params)


def notification(method: str, params: Object | None = None) -> Request:
    return Request(NotSpecified, method, params)


##


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['result', 'error'], omit_if=is_not_specified)
class Response(lang.Final):
    id: Id
    dc.validate(lambda self: self.id is not NotSpecified)

    _: dc.KW_ONLY

    result: ta.Any = dc.field(default=NotSpecified)
    error: ta.Union['Error', type[NotSpecified]] = dc.field(default=NotSpecified)
    dc.validate(lambda self: is_not_specified(self.result) ^ is_not_specified(self.error))

    jsonrpc: str = dc.field(default=VERSION)
    dc.validate(lambda self: self.jsonrpc == VERSION)


def result(id: Id, result: ta.Any) -> Response:  # noqa
    return Response(id, result=result)


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['data'], omit_if=is_not_specified)
class Error(lang.Final):
    code: int
    message: str
    data: ta.Any = NotSpecified


def error(id: Id, error: Error) -> Response:  # noqa
    return Response(id, error=error)
