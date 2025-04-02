"""
Request : Option
Response : Detail

TODO:
 - try: unique class kwarg on TypedValue? modifies bases... don't want a metaclass
  - no, fucks up type inference in TypedValues collection overload
 - @ta.overload
"""
import abc
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from .typedvalues import ScalarTypedValue
from .typedvalues import TypedValue
from .typedvalues import TypedValues


T = ta.TypeVar('T')

OptionT = ta.TypeVar('OptionT', bound='Option')
RequestT = ta.TypeVar('RequestT', bound='Request')

DetailT = ta.TypeVar('DetailT', bound='Detail')
ResponseT = ta.TypeVar('ResponseT', bound='Response')


##


class Option(TypedValue, lang.Abstract):
    pass


class ScalarOption(ScalarTypedValue[T], Option, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Request(lang.Abstract, ta.Generic[OptionT]):
    options: TypedValues[OptionT] | None = dc.field(default=None, kw_only=True)


#


class Detail(TypedValue, lang.Abstract):
    pass


class ScalarDetail(ScalarTypedValue[T], Detail, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Response(lang.Abstract, ta.Generic[DetailT]):
    details: TypedValues[DetailT] | None = dc.field(default=None, kw_only=True)


#


class Service(lang.Abstract, ta.Generic[RequestT, ResponseT]):
    @abc.abstractmethod
    def invoke(self, request: RequestT) -> ResponseT:
        raise NotImplementedError


##


class FooOption(Option, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class FooRequest(Request):
    input_foo_str: str


class FooDetail(Detail, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class FooResponse(Response):
    output_foo_str: str


class FooService(Service[FooRequest, FooResponse]):
    def invoke(self, request: FooRequest) -> FooResponse:
        return FooResponse(request.input_foo_str + '!')


##


def _main() -> None:
    foo_svc = FooService()

    foo_req = FooRequest('foo')
    print(foo_req)

    foo_resp = foo_svc.invoke(foo_req)
    print(foo_resp)


if __name__ == '__main__':
    _main()
