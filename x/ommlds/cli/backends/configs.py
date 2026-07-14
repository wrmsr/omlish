from omcore import dataclasses as dc
from omcore import lang


with lang.auto_proxy_import(globals()):
    from ... import minichain as mc


##


@dc.dataclass(frozen=True, kw_only=True)
class BackendConfig:
    backend: str | mc.BackendSpec | None = None
