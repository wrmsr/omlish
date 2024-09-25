"""
TODO:
 - extract
 - shell
 - checksum
"""
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from .consts import SERIALIZATION_VERSION


##


@dc.dataclass(frozen=True)
class Action(lang.Abstract, lang.Sealed):
    serialization_version: int = dc.field(default=SERIALIZATION_VERSION, kw_only=True)


##


def _non_empty_strs(v: ta.Sequence[str]) -> ta.Sequence[str]:
    return [check.non_empty_str(s) for s in ([v] if isinstance(v, str) else v)]


@dc.dataclass(frozen=True)
class ExtractAction(Action, lang.Final):
    files: ta.Sequence[str] = dc.xfield(coerce=_non_empty_strs)
    keep_archive: bool = False


##


@lang.static_init
def _install_standard_marshalling() -> None:
    actions_poly = msh.polymorphism_from_subclasses(Action, naming=msh.Naming.SNAKE, strip_suffix=True)
    msh.STANDARD_MARSHALER_FACTORIES[0:0] = [msh.PolymorphismMarshalerFactory(actions_poly)]
    msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [msh.PolymorphismUnmarshalerFactory(actions_poly)]
