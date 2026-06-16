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
    def tabledef_renderer(self) -> _tabledefs.PostgresTabledefRenderer:
        return _tabledefs.PostgresTabledefRenderer()

    @property
    def inspector(self) -> _inspect.PostgresInspector:
        return _inspect.PostgresInspector()
