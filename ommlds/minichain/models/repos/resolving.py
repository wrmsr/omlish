import abc
import typing as ta

from omlish import lang

from ..configs import ModelRepo


##


class ResolvedModelRepo(ta.NamedTuple):
    path: str


class ModelRepoResolver(lang.Abstract):
    @abc.abstractmethod
    def can_resolve(self, repo: ModelRepo) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def resolve(self, repo: ModelRepo) -> ResolvedModelRepo | None:
        raise NotImplementedError
