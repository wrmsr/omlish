import dataclasses as dc
import typing as ta

from .... import lang
from ...api.configs import Config
from ...api.configs import ConfigRegistry


##


@dc.dataclass(frozen=True, eq=False)
class LazyInit(Config, lang.Final):
    fn: ta.Callable[[ConfigRegistry], None]
