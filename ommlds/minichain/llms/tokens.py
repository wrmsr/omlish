import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh


msh.register_global_module_import('._marshal', __package__)


##


Token: ta.TypeAlias = int


@dc.dataclass(frozen=True)
class Tokens(lang.Final):
    l: ta.Sequence[Token]
