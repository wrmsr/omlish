import typing as ta

from omlish import lang

from .services import Option
from .services import Request
from .services import Response
from .services import Service


RequestT = ta.TypeVar('RequestT', bound='Request')
ResponseT = ta.TypeVar('ResponseT', bound='Response')
NewT = ta.TypeVar('NewT')
OptionT = ta.TypeVar('OptionT', bound='Option')


class WrapperService(
    Service[
        RequestT,
        OptionT,
        NewT,
        ResponseT,
    ],
    lang.Abstract,
):
    def __init__(self, underlying: Service) -> None:
        super().__init__()
        self._underlying = underlying

    @property
    def underlying(self) -> Service[RequestT, OptionT, NewT, ResponseT]:
        return self._underlying

    @property
    def request_cls(self) -> type[Request]:  # type: ignore[override]
        return self._underlying.request_cls

    @property
    def option_cls_set(self) -> frozenset[type[Option]]:  # type: ignore[override]
        return self._underlying.option_cls_set

    @property
    def new_request_cls(self) -> ta.Any:
        return self._underlying.new_request_cls

    @property
    def response_cls(self) -> type[Response]:  # type: ignore[override]
        return self._underlying.response_cls

    def invoke(self, request: RequestT) -> ResponseT:
        return self._underlying.invoke(request)
