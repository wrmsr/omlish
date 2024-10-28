import typing as ta

from omlish import lang

from .options import Option
from .services import Service
from .services import ServiceRequest
from .services import ServiceResponse


ServiceRequestT = ta.TypeVar('ServiceRequestT', bound='ServiceRequest')
ServiceOptionT = ta.TypeVar('ServiceOptionT', bound='Option')
ServiceNewT = ta.TypeVar('ServiceNewT')
ServiceResponseT = ta.TypeVar('ServiceResponseT', bound='ServiceResponse')


class WrapperService(
    Service[
        ServiceRequestT,
        ServiceOptionT,
        ServiceNewT,
        ServiceResponseT,
    ],
    lang.Abstract,
):
    def __init__(self, underlying: Service) -> None:
        super().__init__()
        self._underlying = underlying

    @property
    def underlying(self) -> Service[ServiceRequestT, ServiceOptionT, ServiceNewT, ServiceResponseT]:
        return self._underlying

    @property
    def request_cls(self) -> type[ServiceRequest]:  # type: ignore[override]
        return self._underlying.request_cls

    @property
    def option_cls_set(self) -> frozenset[type[Option]]:  # type: ignore[override]
        return self._underlying.option_cls_set

    @property
    def new_cls(self) -> ta.Any:
        return self._underlying.new_cls

    @property
    def response_cls(self) -> type[ServiceResponse]:  # type: ignore[override]
        return self._underlying.response_cls

    def invoke(self, request: ServiceRequestT) -> ServiceResponseT:
        return self._underlying.invoke(request)
