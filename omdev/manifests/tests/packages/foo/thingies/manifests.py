import dataclasses as dc

from omlish.manifests.base import ModAttrManifest
from omlish.manifests.base import NameAliasesManifest


##


@dc.dataclass(frozen=True)
class SimpleThingyManifest:
    what: str


@dc.dataclass(frozen=True, kw_only=True)
class NamedThingyManifest(NameAliasesManifest, ModAttrManifest):
    pass
