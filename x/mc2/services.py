import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .typedvalues import ScalarTypedValue
from .typedvalues import TypedValue
from .typedvalues import TypedValueContainer
from .typedvalues import TypedValues


T = ta.TypeVar('T')

RequestOptionT = ta.TypeVar('RequestOptionT', bound='RequestOption')
RequestT = ta.TypeVar('RequestT', bound='Request')
RequestT_contra = ta.TypeVar('RequestT_contra', bound='Request', contravariant=True)

ResponseOutputT = ta.TypeVar('ResponseOutputT', bound='ResponseOutput')
ResponseT = ta.TypeVar('ResponseT', bound='Response')
ResponseT_co = ta.TypeVar('ResponseT_co', bound='Response', covariant=True)


##


class RequestOption(TypedValue, lang.Abstract):
    pass


class ScalarRequestOption(ScalarTypedValue[T], RequestOption, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Request(TypedValueContainer[RequestOptionT], lang.Abstract):
    options: TypedValues[RequestOptionT] | None = dc.field(default=None, kw_only=True)

    @property
    def _typed_values(self) -> TypedValues[RequestOptionT] | None:
        return self.options


#


class ResponseOutput(TypedValue, lang.Abstract):
    pass


class ScalarResponseOutput(ScalarTypedValue[T], ResponseOutput, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Response(TypedValueContainer[ResponseOutputT], lang.Abstract):
    outputs: TypedValues[ResponseOutputT] | None = dc.field(default=None, kw_only=True)

    @property
    def _typed_values(self) -> TypedValues[ResponseOutputT] | None:
        return self.outputs


#


@ta.runtime_checkable
class Service(ta.Protocol[RequestT_contra, ResponseT_co]):
    def invoke(self, request: RequestT_contra) -> ResponseT_co: ...


@lang.protocol_check(Service)
class Service_(lang.Abstract, ta.Generic[RequestT, ResponseT]):  # noqa
    @abc.abstractmethod
    def invoke(self, request: RequestT) -> ResponseT:
        raise NotImplementedError
