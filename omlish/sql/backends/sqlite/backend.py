from .... import lang
from ..base import Backend


with lang.auto_proxy_import(globals()):
    from . import dialect as _dialect
    from . import inspect as _inspect
    from . import tabledefs as _tabledefs


##


class SqliteBackend(Backend, lang.Final):
    @property
    def dialect(self) -> _dialect.SqliteDialect:
        return _dialect.SqliteDialect()

    @property
    def statement_renderer(self) -> _tabledefs.SqliteStatementRenderer:
        return _tabledefs.SqliteStatementRenderer()

    @property
    def inspector(self) -> _inspect.SqliteInspector:
        return _inspect.SqliteInspector()
