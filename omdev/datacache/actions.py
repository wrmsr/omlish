import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from .consts import SERIALIZATION_VERSION


##


@dc.dataclass(frozen=True)
class Action(lang.Abstract, lang.Sealed):
    serialization_version: int = dc.field(default=SERIALIZATION_VERSION, kw_only=True)


##


@dc.dataclass(frozen=True)
class ExtractAction(Action, lang.Final):
    files: ta.Sequence[str]


##


@lang.cached_function
def _install_standard_marshalling() -> None:
    actions_poly = msh.polymorphism_from_subclasses(Action)
    msh.STANDARD_MARSHALER_FACTORIES[0:0] = [msh.PolymorphismMarshalerFactory(actions_poly)]
    msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [msh.PolymorphismUnmarshalerFactory(actions_poly)]


_install_standard_marshalling()
