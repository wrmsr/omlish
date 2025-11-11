from omlish import dataclasses as dc


##


@dc.dataclass(frozen=True, kw_only=True)
class BackendConfig:
    backend: str | None = None
