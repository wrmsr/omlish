import typing as ta

from omlish import lang

from .requests import RequestT_contra
from .responses import ResponseT_co


##


@ta.runtime_checkable
class Service(lang.ProtocolForbiddenAsBaseClass, ta.Protocol[RequestT_contra, ResponseT_co]):
    def invoke(self, request: RequestT_contra) -> ta.Awaitable[ResponseT_co]: ...
