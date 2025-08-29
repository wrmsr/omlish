import dataclasses as dc

from .... import lang
from ...base.configs import Config


##


@dc.dataclass(frozen=True, eq=False)
class ModuleImport(Config, lang.Final):
    name: str
    package: str | None = None
