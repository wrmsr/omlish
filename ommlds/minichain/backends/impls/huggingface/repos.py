"""
TODO:
 - local-only check first
  - cat ~/.cache/.../models/.../refs/main -> c5bfd839cd4cda0e5a39a97e00218d9c56e468af
"""
from omlish import lang

from ....models.configs import ModelRepo
from ....models.repos.resolving import ModelRepoResolver
from ....models.repos.resolving import ResolvedModelRepo


with lang.auto_proxy_import(globals()):
    import huggingface_hub as hf


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
