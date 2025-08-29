from ... import dataclasses as dc
from ... import lang
from ... import reflect as rfl
from .registries import RegistryItem
from .types import Marshaler
from .types import MarshalerFactory
from .types import Unmarshaler
from .types import UnmarshalerFactory


##


@dc.dataclass(frozen=True, kw_only=True)
class Override(RegistryItem, lang.Final):
    marshaler: Marshaler | None = dc.xfield(None, check_type=(Marshaler, None))
    marshaler_factory: MarshalerFactory | None = None

    unmarshaler: Unmarshaler | None = dc.xfield(None, check_type=(Unmarshaler, None))
    unmarshaler_factory: UnmarshalerFactory | None = None


@dc.dataclass(frozen=True)
class ReflectOverride(RegistryItem, lang.Final):
    rty: rfl.Type
