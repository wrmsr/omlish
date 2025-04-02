"""
Request : Option
Response : Detail

TODO:
 - try: unique class kwarg on TypedValue? modifies bases... don't want a metaclass
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

RequestT = ta.TypeVar('RequestT', bound='Request')
ResponseT = ta.TypeVar('ResponseT', bound='Response')


##


class Option(TypedValue, lang.Abstract):
    pass


class ScalarOption(ScalarTypedValue[T], Option, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Request(lang.Abstract):
    options: TypedValues[Option] | None = dc.field(default=None, kw_only=True)


#


class Detail(TypedValue, lang.Abstract):
    pass


class ScalarDetail(ScalarTypedValue[T], Detail, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Response(lang.Abstract):
    details: TypedValues[Detail] | None = dc.field(default=None, kw_only=True)


#


class Service(lang.Abstract, ta.Generic[RequestT, ResponseT]):
    @abc.abstractmethod
    def invoke(self, request: RequestT) -> ResponseT:
        raise NotImplementedError


##


def _main() -> None:
    pass


if __name__ == '__main__':
    _main()
