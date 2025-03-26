import typing as ta

from omlish import lang

from .options import Option  # noqa
from .services import Service
from .services import ServiceRequest  # noqa
from .services import ServiceResponse  # noqa


ServiceRequestT = ta.TypeVar('ServiceRequestT', bound='ServiceRequest')
ServiceOptionT = ta.TypeVar('ServiceOptionT', bound='Option')
ServiceNewT = ta.TypeVar('ServiceNewT')
ServiceResponseT = ta.TypeVar('ServiceResponseT', bound='ServiceResponse')


##


class StreamServiceResponse(
    ServiceResponse[ta.Iterator[ServiceResponseT]],
    ta.Iterator[ServiceResponseT],
):
    def __enter__(self) -> ta.Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None

    def __next__(self) -> ServiceResponseT:
        return next(self.v)


class StreamService(  # noqa
    Service[
        ServiceRequestT,
        ServiceOptionT,
        ServiceNewT,
        StreamServiceResponse[ServiceResponseT],
    ],
    lang.Abstract,
):
    pass
