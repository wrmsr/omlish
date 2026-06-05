import typing as ta

from omlish import dataclasses as dc
from omlish import lang


with lang.auto_proxy_import(globals()):
    from ... import minichain as mc


##


@dc.dataclass(frozen=True, kw_only=True)
class BackendConfig:
    backend: str | None = None

    configs: ta.Sequence[mc.Config] | None = None
