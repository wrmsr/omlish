import dataclasses as dc
import importlib
import sys

from .... import lang
from ...base.configs import Config


##


@dc.dataclass(frozen=True, eq=False)
class ModuleImport(Config, lang.Final):
    name: str
    package: str | None = None

    @lang.cached_function
    def resolve(self) -> str:
        return lang.resolve_import_name(self.name, self.package)

    def import_if_necessary(self) -> bool:
        if (mn := self.resolve()) in sys.modules:
            return False

        importlib.import_module(mn)
        return True
