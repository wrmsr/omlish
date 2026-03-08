import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .modules.configs import ModuleConfig


##


@dc.dataclass(frozen=True, kw_only=True)
class SessionConfig(lang.Abstract):
    modules: ta.Sequence[ModuleConfig] | None = None
