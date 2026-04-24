import abc
import typing as ta

from omlish import check
from omlish import lang
from omlish import reflect as rfl

from .services import Service


ServiceT = ta.TypeVar('ServiceT', bound=Service)


##


class ServiceOfProvider(lang.Abstract):
    @abc.abstractmethod
    def provide_service_of(self, service_cls: ta.Any) -> ta.AsyncContextManager[Service]:
        raise NotImplementedError


##


class ServiceProvider(lang.Abstract, ta.Generic[ServiceT]):
    @abc.abstractmethod
    def provide_service(self) -> ta.AsyncContextManager[ServiceT]:
        raise NotImplementedError


#


class GenericServiceProvider(ServiceProvider[ServiceT]):
    def __init__(self, service_of_provider: ServiceOfProvider) -> None:
        super().__init__()

        self._service_of_provider = service_of_provider

    def provide_service(self) -> ta.AsyncContextManager[ServiceT]:
        rty = rfl.typeof(rfl.get_orig_class(self))
        [service_cls] = check.isinstance(rty, rfl.Generic).args
        return self._service_of_provider.provide_service_of(service_cls)  # type: ignore[return-value]
