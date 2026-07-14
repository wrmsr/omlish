from omcore import dataclasses as dc
from omcore.manifests.base import ModAttrManifest
from omcore.manifests.base import NameAliasesManifest


##


@dc.dataclass(frozen=True, kw_only=True)
class RegistryTypeManifest(ModAttrManifest):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class RegistryManifest(NameAliasesManifest, ModAttrManifest):
    type: str
