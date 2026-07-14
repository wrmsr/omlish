import dataclasses as dc

from omcore.manifests.base import ModAttrManifest
from omcore.manifests.base import NameAliasesManifest


##


@dc.dataclass(frozen=True)
class SimpleThingyManifest:
    what: str


@dc.dataclass(frozen=True, kw_only=True)
class NamedThingyManifest(NameAliasesManifest, ModAttrManifest):
    pass
