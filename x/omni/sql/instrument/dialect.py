import contextlib
import functools
import typing as ta

import sqlalchemy as sa

from ... import check
from ... import lang


class DialectInstrumentation:

    def engine_created(self, engine: sa.engine.Engine) -> None:
        pass

    def connect(self, connect: ta.Callable[..., sa.engine.Connection], *cargs, **cparams) -> sa.engine.Connection:
        return connect(*cargs, **cparams)

    class RewriteMode(lang.AutoEnum):
        EXECUTEMANY = ...
        EXECUTE = ...
        EXECUTE_NO_PARAMS = ...

    @contextlib.contextmanager
    def instrument_statement(self, mode, cursor, statement, parameters, context=None) -> ta.Iterator[str]:
        yield statement


class InstrumentationDialectMixin(sa.engine.Dialect, lang.Abstract):  # noqa

    def __init__(self, instrumentations: ta.Iterable[DialectInstrumentation] = (), **kwargs) -> None:
        super().__init__(**kwargs)  # type: ignore

        self._instrumentations: ta.List[DialectInstrumentation] = [
            check.isinstance(i, DialectInstrumentation) for i in (instrumentations or [])]

    @classmethod
    def dbapi(cls):
        dbapi = super().dbapi()  # noqa
        cls.dbapi = staticmethod(lambda: dbapi)
        return dbapi

    @property
    def instrumentations(self) -> ta.List[DialectInstrumentation]:
        return self._instrumentations

    def connect(self, *cargs, **cparams) -> sa.engine.Connection:
        connect = super().connect
        for inst in self._instrumentations:
            connect = functools.partial(inst.connect, connect)
        return connect(*cargs, **cparams)  # type: ignore

    @contextlib.contextmanager
    def instrument_statement(self, mode, cursor, statement, parameters, context=None) -> ta.Iterator[str]:
        with contextlib.ExitStack() as es:
            for inst in self._instrumentations:
                statement = es.enter_context(inst.instrument_statement(mode, cursor, statement, parameters, context))
            yield statement

    def do_executemany(self, cursor, statement, parameters, context=None):
        with self.instrument_statement(
                DialectInstrumentation.RewriteMode.EXECUTEMANY, cursor, statement, parameters, context
        ) as statement:
            return super().do_executemany(cursor, statement, parameters, context=context)

    def do_execute(self, cursor, statement, parameters, context=None):
        with self.instrument_statement(
                DialectInstrumentation.RewriteMode.EXECUTE, cursor, statement, parameters, context
        ) as statement:
            return super().do_execute(cursor, statement, parameters, context=context)

    def do_execute_no_params(self, cursor, statement, context=None):  # noqa
        with self.instrument_statement(
                DialectInstrumentation.RewriteMode.EXECUTE_NO_PARAMS, cursor, statement, None, context
        ) as statement:
            return super().do_execute_no_params(cursor, statement, context=context)

    class EngineCreatedDescriptor:

        def __get__(self, obj, cls):
            if obj is not None:
                def bound(engine):
                    super(InstrumentationDialectMixin, obj).engine_created(engine)
                    for inst in obj.instrumentations:
                        inst.engine_created(engine)
                return bound
            else:
                def unbound(engine):
                    return engine.dialect.engine_created(engine)
                return unbound

    engine_created = EngineCreatedDescriptor()
