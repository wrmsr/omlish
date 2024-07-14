import abc
import typing as ta

import sqlalchemy as sa
import sqlalchemy.sql.compiler  # noqa
import sqlalchemy.sql.elements  # noqa

from .. import caches
from .. import check
from .. import dataclasses as dc
from .. import interfaces
from .. import properties


K = ta.TypeVar('K')
V = ta.TypeVar('V')

BindParameter = sa.sql.elements.BindParameter

ParamExtractor = ta.Callable[[V], ta.Mapping[BindParameter, ta.Any]]

QueryConstructor = ta.Callable[
    [V, sa.engine.Connection],
    ta.Tuple[sa.sql.Selectable, ta.Dict[sa.sql.elements.BindParameter, ta.Any]]
]


class ParameterizedValue(ta.Generic[V]):

    def __init__(
            self,
            value: V,
            params: ta.Iterable[BindParameter],
            extractors: ta.Iterable[ParamExtractor[V]],
    ) -> None:
        super().__init__()

        self._value = value
        self._params = list(set(params))
        self._extractors = list(extractors)

    @property
    def value(self) -> V:
        return self._value

    @properties.cached
    def params(self) -> ta.List[BindParameter]:
        return self._params

    def extract(self, value: V) -> ta.Dict[BindParameter, ta.Any]:
        ret: ta.Dict[BindParameter, ta.Any] = {}
        for ex in self._extractors:
            for p, v in ex(value).items():
                check.not_in(p, ret)
                ret[p] = v
        return ret


class Parameterizer(ta.Generic[K, V], abc.ABC):

    @abc.abstractmethod
    def key(self, value: V) -> K:
        raise NotImplementedError

    @abc.abstractmethod
    def parameterize(self, key: K) -> ParameterizedValue[V]:
        raise NotImplementedError


class QueryCompilationCache(ta.Generic[K, V]):
    """
    Partially adapted from sqla internals:

        https://github.com/sqlalchemy/sqlalchemy/blob/5881fd274015af3de37f2ff0f91ff6a7c61c1540/lib/sqlalchemy/engine/base.py#L1069
    """

    @dc.dataclass(frozen=True)
    class Entry(ta.Generic[K]):
        key: K
        parameterized: ParameterizedValue

        query: sa.sql.Selectable
        query_params: ta.Dict[sa.sql.elements.BindParameter, ta.Any]

        compiled: sa.sql.compiler.Compiled

    def __init__(
            self,
            parameterizer: Parameterizer[K, V],
            constructor: QueryConstructor[V],
            *,
            metrics: interfaces.MetricsCollection = interfaces.NopMetricsCollection(),
    ) -> None:
        super().__init__()

        self._parameterizer = check.isinstance(parameterizer, Parameterizer)
        self._constructor = check.callable(constructor)
        self._metrics = check.isinstance(metrics, interfaces.MetricsCollection)

        self._cache: ta.MutableMapping[K, QueryCompilationCache.Entry] = caches.new_cache()

    def build(self, key: K, conn: sa.engine.Connection) -> Entry:
        parameterized = self._parameterizer.parameterize(key)

        query, query_params = self._constructor(parameterized.value, conn)

        compiled = query.compile(
            dialect=conn.dialect,
            column_keys=list({p.key for p in [*parameterized.params, *query_params]}),
            schema_translate_map=conn.schema_for_object
            if not conn.schema_for_object.is_default
            else None,
        )

        return QueryCompilationCache.Entry(
            key,
            parameterized,
            query,
            query_params,
            compiled,
        )

    def get(self, key: K, conn: sa.engine.Connection) -> Entry:
        try:
            entry = self._cache[key]
        except KeyError:
            self._metrics.count('miss')
            entry = self._cache[key] = self.build(key, conn)
        else:
            self._metrics.count('hit')
        check.state(entry.key == key)
        return entry

    def extract(self, value: V, entry: Entry) -> ta.Dict[str, ta.Any]:
        params = entry.parameterized.extract(value)
        params.update({p: params[v] if v in params else v for p, v in entry.query_params.items()})
        params = {p.key: list(v) if isinstance(v, set) else v for p, v in params.items()}
        return params

    def dispatch(
            self,
            entry: Entry,
            params: ta.Dict[str, ta.Any],
            conn: sa.engine.Connection,
    ) -> sa.engine.ResultProxy:
        if conn._has_events or conn.engine._has_events:
            for fn in conn.dispatch.before_execute:
                _, _, params = fn(conn, entry.compiled.statement, (), params)

        rows = conn._execute_context(
            conn.dialect,
            conn.dialect.execution_ctx_cls._init_compiled,
            entry.compiled,
            [params],
            entry.compiled,
            [params],
        )

        if conn._has_events or conn.engine._has_events:
            conn.dispatch.after_execute(conn, entry.compiled.statement, (), params, rows)

        return rows

    def execute(self, value: V, conn: sa.engine.Connection) -> sa.engine.ResultProxy:
        key = self._parameterizer.key(value)
        entry = self.get(key, conn)
        params = self.extract(value, entry)
        return self.dispatch(entry, params, conn)
