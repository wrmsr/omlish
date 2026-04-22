import dataclasses as dc
import typing as ta

from ... import lang
from ..api.configs import Config
from ..api.registries import UniqueRegistryItem
from ..api.types import MarshalerFactory
from ..api.types import UnmarshalerFactory


##


@dc.dataclass(frozen=True, eq=False)
class StandardMarshalerFactories(Config, UniqueRegistryItem, lang.Final):
    lst: ta.Sequence[MarshalerFactory]


@dc.dataclass(frozen=True, eq=False)
class StandardUnmarshalerFactories(Config, UniqueRegistryItem, lang.Final):
    lst: ta.Sequence[UnmarshalerFactory]
