import contextlib
import typing as ta

from omlish import lang

from ... import minichain as mc
from .types import BackendConfigs
from .types import BackendName


ServiceT = ta.TypeVar('ServiceT', bound=mc.Service)


##


class ServiceProviderImpl(mc.ServiceProvider[ServiceT]):
    def __init__(
            self,
            service_cls: ta.Any,
            *,
            backend_spec_resolver: mc.BackendSpecResolver | None = None,
            name: BackendName | None = None,
            configs: BackendConfigs | None = None,
    ) -> None:
        super().__init__()

        self._service_cls = service_cls
        if backend_spec_resolver is None:
            backend_spec_resolver = mc.DEFAULT_BACKEND_SPEC_RESOLVER
        self._backend_spec_resolver = backend_spec_resolver
        self._name = name
        self._configs = configs

    @contextlib.asynccontextmanager
    async def provide_service(self) -> ta.AsyncIterator[ServiceT]:
        name: str
        if self._name is not None:
            name = self._name
        else:
            raise RuntimeError('No backend name specified')

        rbs = self._backend_spec_resolver.resolve(
            self._service_cls,
            mc.BackendSpec.of(name),
        )

        async with lang.async_or_sync_maybe_managing(
            await mc.instantiate_backend_spec(
                rbs,
                *(self._configs or []),
            ),
        ) as service:
            yield service


class ServiceOfProviderImpl(mc.ServiceOfProvider):
    def __init__(
            self,
            *,
            backend_spec_resolver: mc.BackendSpecResolver | None = None,
            name: BackendName | None = None,
            configs: BackendConfigs | None = None,
    ) -> None:
        super().__init__()

        if backend_spec_resolver is None:
            backend_spec_resolver = mc.DEFAULT_BACKEND_SPEC_RESOLVER
        self._backend_spec_resolver = backend_spec_resolver
        self._name = name
        self._configs = configs

    @contextlib.asynccontextmanager
    async def provide_service_of(self, service_cls: ta.Any) -> ta.AsyncIterator[mc.Service]:
        name: str
        if self._name is not None:
            name = self._name
        else:
            raise RuntimeError('No backend name specified')

        rbs = self._backend_spec_resolver.resolve(
            service_cls,
            mc.BackendSpec.of(name),
        )

        async with lang.async_or_sync_maybe_managing(
            await mc.instantiate_backend_spec(
                rbs,
                *(self._configs or []),
            ),
        ) as service:
            yield service
