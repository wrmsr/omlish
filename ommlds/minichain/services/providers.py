import abc
import typing as ta

from omlish import check
from omlish import lang
from omlish import reflect2 as rfl

from ..resources import UseResources
from ..types import Option
from ..types import Output
from .requests import Request
from .responses import Response
from .services import Service
from .stream import StreamResponse


ServiceT = ta.TypeVar('ServiceT', bound=Service)


ProxiedRequestV = ta.TypeVar('ProxiedRequestV')
ProxiedOptionT = ta.TypeVar('ProxiedOptionT', bound=Option)

ProxiedResponseV = ta.TypeVar('ProxiedResponseV')
ProxiedOutputT = ta.TypeVar('ProxiedOutputT', bound=Output)

ProxiedStreamOutputT = ta.TypeVar('ProxiedStreamOutputT', bound=Output)


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


class GenericServiceProvider(ServiceProvider[ServiceT]):
    def __init__(self, service_of_provider: ServiceOfProvider) -> None:
        super().__init__()

        self._service_of_provider = service_of_provider

    def provide_service(self) -> ta.AsyncContextManager[ServiceT]:
        rty = rfl.reflect_type(rfl.get_orig_class(self))
        [service_rty] = check.isinstance(rty, rfl.Instance).args
        service_cls = rfl.get_runtime_type(service_rty)
        return self._service_of_provider.provide_service_of(service_cls)  # type: ignore[return-value]


##


class ServiceProviderProxyService(
    ta.Generic[
        ProxiedRequestV,
        ProxiedOptionT,
        ProxiedResponseV,
        ProxiedOutputT,
    ],
):
    def __init__(
        self,
        service_provider: ServiceProvider[
            Service[
                Request[
                    ProxiedRequestV,
                    ProxiedOptionT,
                ],
                Response[
                    ProxiedResponseV,
                    ProxiedOutputT,
                ],
            ],
        ],
    ) -> None:
        super().__init__()

        self._service_provider = service_provider

    async def invoke(
        self,
        request: Request[
            ProxiedRequestV,
            ProxiedOptionT,
        ],
    ) -> Response[
        ProxiedResponseV,
        ProxiedOutputT,
    ]:
        async with self._service_provider.provide_service() as service:
            return await service.invoke(request)


class ServiceProviderProxyStreamService(
    ta.Generic[
        ProxiedRequestV,
        ProxiedOptionT,
        ProxiedResponseV,
        ProxiedOutputT,
        ProxiedStreamOutputT,
    ],
):
    def __init__(
        self,
        service_provider: ServiceProvider[
            Service[
                Request[
                    ProxiedRequestV,
                    ProxiedOptionT,
                ],
                StreamResponse[
                    ProxiedResponseV,
                    ProxiedOutputT,
                    ProxiedStreamOutputT,
                ],
            ],
        ],
    ) -> None:
        super().__init__()

        self._service_provider = service_provider

    async def invoke(
        self,
        request: Request[
            ProxiedRequestV,
            ProxiedOptionT,
        ],
    ) -> StreamResponse[
        ProxiedResponseV,
        ProxiedOutputT,
        ProxiedStreamOutputT,
    ]:
        async with UseResources.or_new(request.options) as rs:
            service = await rs.enter_async_context(self._service_provider.provide_service())
            return await service.invoke(request)
