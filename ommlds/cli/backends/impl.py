import contextlib
import typing as ta

from omlish import check
from omlish import lang
from omlish import reflect as rfl

from ... import minichain as mc
from .types import BackendConfigs
from .types import BackendName
from .types import BackendProvider
from .types import ServiceT


##


class BackendProviderImpl(BackendProvider[ServiceT], lang.Abstract):
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
    async def _provide_backend(self, cls: type[ServiceT]) -> ta.AsyncIterator[ServiceT]:
        name: str
        if self._name is not None:
            name = self._name
        else:
            raise RuntimeError('No backend name specified')

        rbs = self._backend_spec_resolver.resolve(
            cls,
            mc.BackendSpec.of(name),
        )

        service: ServiceT
        async with lang.async_or_sync_maybe_managing(
            mc.instantiate_backend_spec(
                rbs,
                *(self._configs or []),
            ),
        ) as service:
            yield service


##


class GenericBackendProviderImpl(BackendProviderImpl[ServiceT]):
    def provide_backend(self) -> ta.AsyncContextManager[ServiceT]:
        rty = rfl.typeof(rfl.get_orig_class(self))
        [service_cls] = check.isinstance(rty, rfl.Generic).args
        return self._provide_backend(service_cls)  # type: ignore[arg-type]
