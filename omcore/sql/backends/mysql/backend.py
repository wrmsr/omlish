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
    def tabledef_renderer(self) -> _tabledefs.MysqlTabledefRenderer:
        return _tabledefs.MysqlTabledefRenderer()

    @property
    def inspector(self) -> _inspect.MysqlInspector:
        return _inspect.MysqlInspector()
