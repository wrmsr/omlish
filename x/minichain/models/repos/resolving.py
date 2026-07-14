import abc
import typing as ta

from omcore import lang

from ...registries.globals import register_type
from ..configs import ModelRepo


##


class ResolvedModelRepo(ta.NamedTuple):
    path: str


# @om-manifest $.minichain.registries.manifests.RegistryTypeManifest
class ModelRepoResolver(lang.Abstract):
    @abc.abstractmethod
    def can_resolve(self, repo: ModelRepo) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def resolve(self, repo: ModelRepo) -> ResolvedModelRepo | None:
        raise NotImplementedError


register_type(ModelRepoResolver, module=__name__)
