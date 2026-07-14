import typing as ta

from omcore import dataclasses as dc
from omcore import lang

from .. import minichain as mc


##


@dc.dataclass(frozen=True, kw_only=True)
class EntrypointConfig(lang.Abstract):
    modules: ta.Sequence[mc.modules.ModuleConfig] | None = None
