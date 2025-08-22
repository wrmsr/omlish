from ....models.configs import ModelRepo
from ....models.repos.resolving import ModelRepoResolver
from ....models.repos.resolving import ResolvedModelRepo


##


class HuggingfaceModelRepoResolver(ModelRepoResolver):
    def can_resolve(self, repo: ModelRepo) -> bool:
        return True

    def resolve(self, repo: ModelRepo) -> ResolvedModelRepo | None:
        raise NotImplementedError
