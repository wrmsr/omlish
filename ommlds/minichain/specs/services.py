import contextlib
import typing as ta

from omlish import check
from omlish import lang

from ..configs import Config
from ..services import Service
from ..services import ServiceProvider
from .instantiate import DEFAULT_BACKEND_SPEC_INSTANTIATOR
from .resolving import DEFAULT_BACKEND_SPEC_RESOLVER
from .types import BackendSpec
from .types import BackendSpecInstantiator
from .types import BackendSpecResolver
from .types import CanBackendSpec


ServiceT = ta.TypeVar('ServiceT', bound=Service)


##


class BackendSpecServiceProvider(ServiceProvider[ServiceT]):
    def __init__(
            self,
            service_cls: ta.Any,
            spec: CanBackendSpec | ta.Callable[[], CanBackendSpec | ta.Awaitable[CanBackendSpec]],
            *,
            resolver: BackendSpecResolver | None = None,
            instantiator: BackendSpecInstantiator | None = None,
            configs: ta.Sequence[Config] | None = None,
    ) -> None:
        super().__init__()

        self._service_cls = check.not_none(service_cls)
        self._spec = check.not_none(spec)

        if resolver is None:
            resolver = DEFAULT_BACKEND_SPEC_RESOLVER
        self._resolver = resolver
        if instantiator is None:
            instantiator = DEFAULT_BACKEND_SPEC_INSTANTIATOR
        self._instantiator = instantiator
        self._configs = configs

    @contextlib.asynccontextmanager
    async def provide_service(self) -> ta.AsyncIterator[ServiceT]:
        spec: ta.Any = self._spec
        if callable(spec):
            spec = spec()
            if isinstance(spec, ta.Awaitable):
                spec = await spec
        spec = BackendSpec.of(spec)

        rbs = self._resolver.resolve(
            self._service_cls,
            spec,
        )

        async with lang.async_or_sync_maybe_managing(
            await self._instantiator(
                rbs,
                *(self._configs or []),
            ),
        ) as service:
            yield service
