import abc

from omlish import lang

from .index import VectorIndexed
from .search import VectorHits
from .search import VectorSearch
from .similarity import Similarity


class VectorStore(lang.Abstract):
    @abc.abstractmethod
    def index(self, doc: VectorIndexed) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def search(
            self,
            search: VectorSearch,
            *,
            similarity: Similarity | None = None,
    ) -> VectorHits:
        raise NotImplementedError
