import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ... import minichain as mc


##


@dc.dataclass(frozen=True, kw_only=True)
class ModeConfig(lang.Abstract):
    modules: ta.Sequence[mc.modules.ModuleConfig] | None = None
