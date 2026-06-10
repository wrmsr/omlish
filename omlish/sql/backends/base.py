import abc
import typing as ta

from ... import lang


if ta.TYPE_CHECKING:
    from ..api.dialects import Dialect
    from ..inspect.inspectors import Inspector
    from ..tabledefs.rendering import StatementRenderer


##


class Backend(lang.Abstract):
    """
    An optional, fully-deletable convenience grabbag: one object per backend that lazily *provides* the focused facets
    (dialect, the DDL statement renderer, the inspector). Only end-user wiring ever references a Backend - the facets
    themselves stay decomposed and injector-native, and deleting every Backend leaves the codebase running unmodified.
    """

    @property
    @abc.abstractmethod
    def dialect(self) -> Dialect:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def statement_renderer(self) -> StatementRenderer:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def inspector(self) -> Inspector:
        raise NotImplementedError
