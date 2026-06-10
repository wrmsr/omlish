
from .... import lang
from ..base import Backend


with lang.auto_proxy_import(globals()):
    from . import dialect as _dialect
    from . import inspect as _inspect
    from . import tabledefs as _tabledefs


##


class PostgresBackend(Backend, lang.Final):
    @property
    def dialect(self) -> _dialect.PostgresDialect:
        return _dialect.PostgresDialect()

    @property
    def statement_renderer(self) -> _tabledefs.PostgresStatementRenderer:
        return _tabledefs.PostgresStatementRenderer()

    @property
    def inspector(self) -> _inspect.PostgresInspector:
        return _inspect.PostgresInspector()
