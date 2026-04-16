import dataclasses as dc
import importlib
import sys
import typing as ta

from .... import lang
from ...api.configs import Config
from ...api.configs import ConfigRegistry


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
