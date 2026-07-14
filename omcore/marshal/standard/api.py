import dataclasses as dc
import typing as ta

from ... import lang
from ... import typedvalues as tv
from ..api.configs import Config
from ..api.types import MarshalerFactory
from ..api.types import UnmarshalerFactory


##


@dc.dataclass(frozen=True, eq=False)
class StandardMarshalerFactories(Config, tv.UniqueTypedValue, lang.Final):
    lst: ta.Sequence[MarshalerFactory]


@dc.dataclass(frozen=True, eq=False)
class StandardUnmarshalerFactories(Config, tv.UniqueTypedValue, lang.Final):
    lst: ta.Sequence[UnmarshalerFactory]
