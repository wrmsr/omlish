from omlish import dataclasses as dc


##


DEFAULT_BACKEND = 'openai'


##


@dc.dataclass(frozen=True, kw_only=True)
class BackendConfig:
    backend: str | None = None
