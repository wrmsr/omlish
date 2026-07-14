"""
TODO:
 - extract
 - shell
 - checksum
"""
import typing as ta

from omcore import check
from omcore import dataclasses as dc
from omcore import lang
from omcore import marshal as msh

from .consts import SERIALIZATION_VERSION


##


@dc.dataclass(frozen=True)
@msh.set_polymorphic_from_subclasses(naming=msh.Naming.SNAKE, strip_suffix=True)
class Action(lang.Abstract, lang.Sealed):
    serialization_version: int = dc.field(default=SERIALIZATION_VERSION, kw_only=True)


##


def _non_empty_strs(v: ta.Sequence[str]) -> ta.Sequence[str]:
    return [check.non_empty_str(s) for s in ([v] if isinstance(v, str) else v)]


@dc.dataclass(frozen=True)
class ExtractAction(Action, lang.Final):
    files: ta.Sequence[str] = dc.xfield(coerce=_non_empty_strs)
    keep_archive: bool = False
