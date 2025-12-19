from omlish import dataclasses as dc
from omlish import lang


##


@dc.dataclass(frozen=True, kw_only=True)
class SessionConfig(lang.Abstract):
    pass
