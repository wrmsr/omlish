import abc
import typing as ta

from ... import lang
from ..params import ParamStyle
from ..syntax import QuoteStyle
from ..syntax import QuoteStyles
from .columns import Column


if ta.TYPE_CHECKING:
    from ..queries.rendering import Renderer


##


class Adapter(lang.Abstract):
    @property
    @abc.abstractmethod
    def param_style(self) -> ParamStyle | None:
        raise NotImplementedError

    @property
    def quote_style(self) -> QuoteStyle:
        return QuoteStyles.DOUBLE

    @property
    def query_renderer(self) -> type[Renderer] | None:
        """A queries.Renderer subclass for structural dialect divergence, or None to use the standard renderer."""

        return None

    @abc.abstractmethod
    def scan_type(self, c: Column) -> type:
        raise NotImplementedError


##


class HasAdapter(lang.Abstract):
    @property
    @abc.abstractmethod
    def adapter(self) -> Adapter:
        raise NotImplementedError
