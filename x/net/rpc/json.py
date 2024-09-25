"""
https://www.jsonrpc.org/specification
"""
import operator
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish import matchfns as mfs
from omlish import reflect as rfl
from omlish.formats import json


Number: ta.TypeAlias = int | float
Object: ta.TypeAlias = ta.Mapping[str, ta.Any]
Id: ta.TypeAlias = str | Number | None


##


VERSION = '2.0'


class NotSpecified(lang.Marker):
    pass


_NOT_SPECIFIED_RTY = rfl.type_(type[NotSpecified])


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


def request(id: Id, method: str, params: Object | None = None) -> Request:  # noqa
    return Request(id, method, params)


def notification(method: str, params: Object | None = None) -> Request:
    return Request(NotSpecified, method, params)


##


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['result', 'error'], omit_if=is_not_specified)
class Response:
    id: Id

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
class Error:
    code: int
    message: str
    data: ta.Any = NotSpecified


def error(id: Id, error: Error) -> Response:  # noqa
    return Response(id, error=result)

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


@dc.dataclass(frozen=True)
class NotSpecifiedUnionMarshaler(msh.Marshaler):
    m: msh.Marshaler

    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        if o is NotSpecified:
            raise TypeError(o)
        return self.m.marshal(ctx, o)


class NotSpecifiedUnionMarshalerFactory(msh.MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: (
            isinstance(rty, rfl.Union) and
            not rty.is_optional and
            _NOT_SPECIFIED_RTY in rty.args
    ))
    def fn(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        args = set(check.isinstance(rty, rfl.Union).args) - {_NOT_SPECIFIED_RTY}
        nty = rfl.type_(ta.Union[*args])
        m = ctx.make(nty)
        return NotSpecifiedUnionMarshaler(m)


class NotSpecifiedUnionUnmarshalerFactory(msh.UnmarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: (
            isinstance(rty, rfl.Union) and
            not rty.is_optional and
            _NOT_SPECIFIED_RTY in rty.args
    ))
    def fn(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        args = set(check.isinstance(rty, rfl.Union).args) - {_NOT_SPECIFIED_RTY}
        nty = rfl.type_(ta.Union[*args])
        return ctx.make(nty)


@lang.static_init
def _install_standard_marshalling() -> None:
    msh.STANDARD_MARSHALER_FACTORIES[0:0] = [
        msh.ForbiddenTypeMarshalerFactory({_NOT_SPECIFIED_RTY}),
        NotSpecifiedUnionMarshalerFactory(),
    ]
    msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [
        msh.ForbiddenTypeUnmarshalerFactory({_NOT_SPECIFIED_RTY}),
        NotSpecifiedUnionUnmarshalerFactory(),
    ]


##


def _main() -> None:
    for obj in [
        request(0, 'foo'),
        result(0, 'bar'),
    ]:
        m = msh.marshal(obj)
        j = json.dumps(m)
        print(j)
        d = json.loads(j)
        u = msh.unmarshal(d, type(obj))
        print(u)


if __name__ == '__main__':
    _main()
