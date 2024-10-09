from ..vectors import Hits
from ..vectors import Indexed
from ..vectors import Search
from ..vectors.stores import VectorStore


class SqliteVectorStore(VectorStore):

    def index(self, doc: Indexed) -> None:
        raise NotImplementedError

    def search(self, search: Search) -> Hits:
        raise NotImplementedError
