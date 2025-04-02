"""
TODO:
 - try: unique class kwarg on TypedValue? modifies bases... don't want a metaclass
  - no, fucks up type inference in TypedValues collection overload
 - @ta.overload def invoke
 - queryable req/resp type mapping, tv types
 - class TypedValuesContainer(lang.Abstract, ta.Generic[TypedValueT]):
  - figures out parameterization
  - must support Union tv bounds
"""
import typing as ta  # noqa

from omlish import dataclasses as dc
from omlish import lang

from ..services import Request
from ..services import RequestOption
from ..services import Response
from ..services import ResponseOutput
from ..services import ScalarRequestOption
from ..services import Service_
from ..typedvalues import UniqueTypedValue


##


class FooRequestOption(RequestOption, lang.Abstract):
    pass


class FooSuffix(ScalarRequestOption[str], FooRequestOption, UniqueTypedValue, lang.Final):
    pass


@dc.dataclass(frozen=True)
class FooRequest(Request[FooRequestOption]):
    input_foo_str: str


#


class FooResponseOutput(ResponseOutput, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class FooResponse(Response[FooResponseOutput]):
    output_foo_str: str


#


class FooService(Service_[FooRequest, FooResponse], request=FooRequest, response=FooResponse):
    def invoke(self, request: FooRequest) -> FooResponse:
        return FooResponse(request.input_foo_str + request.get(FooSuffix('!')).v)


##


def _main() -> None:
    foo_svc = FooService()

    for foo_req in [
        FooRequest('foo'),
        FooRequest('foo').with_options(FooSuffix('?')),
        FooRequest.new('foo', FooSuffix('*')),
    ]:
        print(foo_req)

        foo_resp = foo_svc.invoke(foo_req)
        print(foo_resp)

    foo_resp = foo_svc('foo')
    print(foo_resp)


if __name__ == '__main__':
    _main()
