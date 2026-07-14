import typing as ta

from ...api.dialects import Dialect
from ...syntax import QuoteStyle
from ...syntax import QuoteStyles
from .queries import MysqlRenderer


if ta.TYPE_CHECKING:
    from ...queries.rendering import Renderer


##


class MysqlDialect(Dialect):
    @property
    def quote_style(self) -> QuoteStyle:
        return QuoteStyles.BACKTICK

    @property
    def query_renderer(self) -> type[Renderer] | None:
        return MysqlRenderer

    # supports_returning stays False - mysql has no RETURNING; auto keys come from last_insert_id() instead.

    @property
    def last_insert_id_query(self) -> str | None:
        return 'select last_insert_id()'
