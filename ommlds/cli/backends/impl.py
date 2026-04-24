import contextlib
import typing as ta

from omlish import lang

from ... import minichain as mc
from .types import BackendConfigs
from .types import BackendInstantiator
from .types import BackendName
from .types import BackendProvider
from .types import ChatChoicesServiceBackendProvider
from .types import ChatChoicesStreamServiceBackendProvider
from .types import CompletionServiceBackendProvider
from .types import EmbeddingServiceBackendProvider
from .types import ServiceT


##


class BackendInstantiatorImpl(BackendInstantiator):
    def __init__(
            self,
            *,
            backend_spec_resolver: mc.BackendSpecResolver | None = None,
    ) -> None:
        super().__init__()

        if backend_spec_resolver is None:
            backend_spec_resolver = mc.DEFAULT_BACKEND_SPEC_RESOLVER
        self._backend_spec_resolver = backend_spec_resolver

    async def new_backend(
            self,
            service_cls: ta.Any,
            spec: mc.CanBackendSpec,
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> ta.Any:
        rbs = self._backend_spec_resolver.resolve(
            service_cls,
            mc.BackendSpec.of(spec),
        )

        return mc.instantiate_backend_spec(rbs, *args, **kwargs)


##


class BackendProviderImpl(BackendProvider[ServiceT], lang.Abstract):
    def __init__(
            self,
            *,
            instantiator: BackendInstantiator,
            name: BackendName | None = None,
            configs: BackendConfigs | None = None,
    ) -> None:
        super().__init__()

        self._instantiator = instantiator
        self._name = name
        self._configs = configs

    @contextlib.asynccontextmanager
    async def _provide_backend(self, cls: type[ServiceT]) -> ta.AsyncIterator[ServiceT]:
        name: str
        if self._name is not None:
            name = self._name
        else:
            raise RuntimeError('No backend name specified')

        service: ServiceT
        async with lang.async_or_sync_maybe_managing(
                await self._instantiator.new_backend(
                    cls,
                    name,
                    *(self._configs or []),
                ),
        ) as service:
            yield service


##


class ChatChoicesServiceBackendProviderImpl(
    BackendProviderImpl['mc.ChatChoicesService'],
    ChatChoicesServiceBackendProvider,
):
    def provide_backend(self) -> ta.AsyncContextManager[mc.ChatChoicesService]:
        return self._provide_backend(mc.ChatChoicesService)  # type: ignore[type-abstract]


class ChatChoicesStreamServiceBackendProviderImpl(
    BackendProviderImpl['mc.ChatChoicesStreamService'],
    ChatChoicesStreamServiceBackendProvider,
):
    def provide_backend(self) -> ta.AsyncContextManager[mc.ChatChoicesStreamService]:
        return self._provide_backend(mc.ChatChoicesStreamService)  # type: ignore[type-abstract]


class CompletionServiceBackendProviderImpl(
    BackendProviderImpl['mc.CompletionService'],
    CompletionServiceBackendProvider,
):
    def provide_backend(self) -> ta.AsyncContextManager[mc.CompletionService]:
        return self._provide_backend(mc.CompletionService)  # type: ignore[type-abstract]


class EmbeddingServiceBackendProviderImpl(
    BackendProviderImpl['mc.EmbeddingService'],
    EmbeddingServiceBackendProvider,
):
    def provide_backend(self) -> ta.AsyncContextManager[mc.EmbeddingService]:
        return self._provide_backend(mc.EmbeddingService)  # type: ignore[type-abstract]
