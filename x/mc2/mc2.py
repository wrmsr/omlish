"""
Request : Option
Response : Detail

TODO:
 - try: unique class kwarg on TypedValue? modifies bases... don't want a metaclass
  - no, fucks up type inference in TypedValues collection overload
 - @ta.overload def invoke
 - queryable req/resp type mapping, tv types
 - class TypedValuesContainer(lang.Abstract, ta.Generic[TypedValueT]):
  - figures out parameterization
  - must support Union tv bounds
"""
import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .typedvalues import ScalarTypedValue
from .typedvalues import TypedValue
from .typedvalues import TypedValueContainer
from .typedvalues import TypedValues


T = ta.TypeVar('T')

OptionT = ta.TypeVar('OptionT', bound='Option')
RequestT = ta.TypeVar('RequestT', bound='Request')
RequestT_contra = ta.TypeVar('RequestT_contra', bound='Request', contravariant=True)

DetailT = ta.TypeVar('DetailT', bound='Detail')
ResponseT = ta.TypeVar('ResponseT', bound='Response')
ResponseT_co = ta.TypeVar('ResponseT_co', bound='Response', covariant=True)


##


class Option(TypedValue, lang.Abstract):
    pass


class ScalarOption(ScalarTypedValue[T], Option, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Request(TypedValueContainer[OptionT], lang.Abstract):
    options: TypedValues[OptionT] | None = dc.field(default=None, kw_only=True)

    @property
    def _typed_values(self) -> TypedValues[OptionT] | None:
        return self.options


#


class Detail(TypedValue, lang.Abstract):
    pass


class ScalarDetail(ScalarTypedValue[T], Detail, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Response(TypedValueContainer[DetailT], lang.Abstract):
    details: TypedValues[DetailT] | None = dc.field(default=None, kw_only=True)

    @property
    def _typed_values(self) -> TypedValues[DetailT] | None:
        return self.details


#


@ta.runtime_checkable
class Service(ta.Protocol[RequestT_contra, ResponseT_co]):
    def invoke(self, request: RequestT_contra) -> ResponseT_co: ...


@lang.protocol_check(Service)
class Service_(lang.Abstract, ta.Generic[RequestT, ResponseT]):  # noqa
    @abc.abstractmethod
    def invoke(self, request: RequestT) -> ResponseT:
        raise NotImplementedError


##


class FooOption(Option, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class FooRequest(Request[FooOption]):
    input_foo_str: str


class FooDetail(Detail, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class FooResponse(Response[FooDetail]):
    output_foo_str: str


class FooService(Service_[FooRequest, FooResponse]):
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
