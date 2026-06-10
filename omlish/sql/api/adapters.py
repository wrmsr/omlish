import abc
import typing as ta

from ... import lang
from ..params import ParamStyle
from ..syntax import QuoteStyle
from .columns import Column
from .dialects import STANDARD_DIALECT
from .dialects import Dialect


if ta.TYPE_CHECKING:
    from ..queries.rendering import Renderer


##


class Adapter(lang.Abstract):
    @property
    @abc.abstractmethod
    def param_style(self) -> ParamStyle | None:
        raise NotImplementedError

    @property
    def dialect(self) -> Dialect:
        return STANDARD_DIALECT

    @property
    def quote_style(self) -> QuoteStyle:
        return self.dialect.quote_style

    @property
    def query_renderer(self) -> type[Renderer] | None:
        return self.dialect.query_renderer

    @property
    def supports_returning(self) -> bool:
        return self.dialect.supports_returning

    @property
    def last_insert_id_query(self) -> str | None:
        return self.dialect.last_insert_id_query

    @abc.abstractmethod
    def scan_type(self, c: Column) -> type:
        raise NotImplementedError


##


class HasAdapter(lang.Abstract):
    @property
    @abc.abstractmethod
    def adapter(self) -> Adapter:
        raise NotImplementedError
