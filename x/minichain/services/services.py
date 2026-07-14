import typing as ta

from omlish import lang

from .requests import RequestT_contra
from .responses import ResponseT_co


##


@ta.runtime_checkable
class Service(lang.ProtocolForbiddenAsBaseClass, ta.Protocol[RequestT_contra, ResponseT_co]):
    """
    Universal service protocol, comprised of a single method `invoke`, accepting a request of type `RequestT_contra` and
    returning a response of type `ResponseT_co`.

    Refer to the package README.md for an explanation of its type var variance.

    This class is final, but each instance's `__orig_class__` (if present) is significant.
    """

    def invoke(self, request: RequestT_contra) -> ta.Awaitable[ResponseT_co]: ...
