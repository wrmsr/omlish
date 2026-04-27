from ..... import minichain as mc
from .configs import DEFAULT_BACKEND
from .types import InitialBackendSpec


##


class BackendManager:
    def __init__(
            self,
            *,
            initial_backend_spec: InitialBackendSpec | None = None,
            resolver: mc.BackendSpecResolver | None = None,
    ) -> None:
        super().__init__()

        if initial_backend_spec is None:
            initial_backend_spec = InitialBackendSpec(mc.BackendSpec.of(DEFAULT_BACKEND))
        self._initial_backend_spec = initial_backend_spec
        if resolver is None:
            resolver = mc.DEFAULT_BACKEND_SPEC_RESOLVER
        self._resolver = resolver

        # FIXME: swallows configs
        # rbs = self._resolver.resolve(mc.ChatChoicesService, initial_backend_spec)  # FIXME: lol

        self._backend_spec: mc.BackendSpec = initial_backend_spec

    async def get_backend_spec(self) -> mc.BackendSpec:
        return self._backend_spec

    async def set_backend_spec(self, backend_spec: mc.CanBackendSpec) -> mc.BackendSpec:
        bs = mc.BackendSpec.of(backend_spec)

        # FIXME: swallows configs
        # rbs = self._resolver.resolve(mc.ChatChoicesService, bs)  # FIXME: lol
        # bs = rbs.spec

        self._backend_spec = bs
        return bs
