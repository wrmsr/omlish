"""
TODO:
 - local-only check first
  - cat ~/.cache/.../models/.../refs/main -> c5bfd839cd4cda0e5a39a97e00218d9c56e468af
"""
import typing as ta

from omlish import lang

from ....models.configs import ModelRepo
from ....models.repos.resolving import ModelRepoResolver
from ....models.repos.resolving import ResolvedModelRepo


if ta.TYPE_CHECKING:
    import huggingface_hub as hf
else:
    hf = lang.proxy_import('huggingface_hub')


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='huggingface',
#     aliases=['hf'],
#     type='ModelRepoResolver',
# )
class HuggingfaceModelRepoResolver(ModelRepoResolver):
    def can_resolve(self, repo: ModelRepo) -> bool:
        return True

    def resolve(self, repo: ModelRepo) -> ResolvedModelRepo | None:
        return ResolvedModelRepo(hf.snapshot_download(repo.slashed))
