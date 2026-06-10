import typing as ta

from ... import lang
from ..syntax import QuoteStyle
from ..syntax import QuoteStyles


if ta.TYPE_CHECKING:
    from ..queries.rendering import Renderer


##


class Dialect(lang.Abstract):
    """
    The driver-independent facets of a backend's SQL dialect: quoting, the (DML) renderer, and capability flags. A
    Dialect knows nothing of drivers (param style, scan types live on the Adapter) nor of the heavier tabledefs/inspect
    facets (those live on the Backend grabbag) - keeping it small and on the load-bearing rendering path.
    """

    @property
    def quote_style(self) -> QuoteStyle:
        return QuoteStyles.DOUBLE

    @property
    def query_renderer(self) -> type[Renderer] | None:
        return None

    @property
    def supports_returning(self) -> bool:
        return False

    @property
    def last_insert_id_query(self) -> str | None:
        # A self-contained query returning the connection's last auto-generated id, for backends without RETURNING.
        return None


class StandardDialect(Dialect, lang.Final):
    pass


STANDARD_DIALECT = StandardDialect()
