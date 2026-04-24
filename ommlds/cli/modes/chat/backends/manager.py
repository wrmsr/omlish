from ..... import minichain as mc
from .types import DEFAULT_BACKEND
from .types import InitialBackendSpec


##


class BackendManager:
    def __init__(
            self,
            *,
            initial_backend_spec: InitialBackendSpec | None = None,
    ) -> None:
        super().__init__()

        if initial_backend_spec is None:
            initial_backend_spec = InitialBackendSpec(mc.BackendSpec.of(DEFAULT_BACKEND))
        self._initial_backend_spec = initial_backend_spec

        self._backend_spec: mc.BackendSpec = initial_backend_spec

    async def get_backend_spec(self) -> mc.BackendSpec:
        return self._backend_spec
