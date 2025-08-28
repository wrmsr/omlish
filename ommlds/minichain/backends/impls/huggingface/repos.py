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
