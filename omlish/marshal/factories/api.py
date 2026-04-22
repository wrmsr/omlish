import dataclasses as dc
import importlib
import sys
import typing as ta

from ... import check
from ... import lang
from ..api.configs import Config
from ..api.configs import ConfigRegistry
from ..api.registries import UniqueRegistryItem
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory


LazyInitFn: ta.TypeAlias = ta.Callable[[ConfigRegistry], None]


##


@dc.dataclass(frozen=True, eq=False)
class LazyInit(Config, lang.Final):
    fn: LazyInitFn


##


@dc.dataclass(frozen=True, eq=False)
class ModuleImport(lang.Final):
    name: str
    package: str | None = None

    def __call__(self, cfgs: ConfigRegistry) -> None:  # noqa
        mn = lang.resolve_import_name(self.name, self.package)

        if mn in sys.modules:
            return

        importlib.import_module(mn)


##


@dc.dataclass(frozen=True, kw_only=True)
class Override(Config, UniqueRegistryItem, lang.Final):
    marshaler: Marshaler | None = None
    marshaler_factory: MarshalerFactory | None = None

    unmarshaler: Unmarshaler | None = None
    unmarshaler_factory: UnmarshalerFactory | None = None

    fallback: bool = False

    def __post_init__(self) -> None:
        check.isinstance(self.marshaler, (Marshaler, None))
        check.isinstance(self.marshaler_factory, (MarshalerFactory, None))

        check.isinstance(self.unmarshaler, (Unmarshaler, None))
        check.isinstance(self.unmarshaler_factory, (UnmarshalerFactory, None))

        check.state(not (self.marshaler is not None and self.marshaler_factory is not None))
        check.state(not (self.unmarshaler is not None and self.unmarshaler_factory is not None))
