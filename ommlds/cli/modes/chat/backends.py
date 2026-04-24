import typing as ta

from omlish import lang

from .... import minichain as mc


##


DEFAULT_BACKEND = 'openai'


InitialBackendSpec = ta.NewType('InitialBackendSpec', mc.BackendSpec)


class BackendSpecGetter(lang.AsyncCachedFunc0[mc.BackendSpec]):
    pass


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
