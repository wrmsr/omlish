from .... import lang
from ..base import Backend


with lang.auto_proxy_import(globals()):
    from . import dialect as _dialect
    from . import inspect as _inspect
    from . import tabledefs as _tabledefs


##


class MysqlBackend(Backend, lang.Final):
    @property
    def dialect(self) -> _dialect.MysqlDialect:
        return _dialect.MysqlDialect()

    @property
    def statement_renderer(self) -> _tabledefs.MysqlStatementRenderer:
        return _tabledefs.MysqlStatementRenderer()

    @property
    def inspector(self) -> _inspect.MysqlInspector:
        return _inspect.MysqlInspector()
