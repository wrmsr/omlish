import functools
import typing as ta

from ... import check
from ... import dataclasses as dc
from .adapters import Adapter
from .queries import ManyParams
from .queries import NoParams
from .queries import Query
from .queries import Queryable
from .queries import QueryMode
from .queries import QueryParams
from .queries import RowParams


##


@dc.dataclass(frozen=True, kw_only=True)
class AsQueryContext:
    mode: QueryMode | str | None = None
    adapter: Adapter | None = None


def _coerce_row_params(params: ta.Any) -> QueryParams:
    if params is None:
        return NoParams()
    elif isinstance(params, QueryParams):
        return params
    else:
        return RowParams(params)


##


def as_query(
        obj: ta.Any,
        params: ta.Any = None,
        /,
        *,
        mode: QueryMode | str | None = None,
        adapter: Adapter | None = None,
) -> Queryable:
    return as_query_(
        obj,
        params,
        ctx=AsQueryContext(
            mode=mode,
            adapter=adapter,
        ),
    )


@functools.singledispatch
def as_query_(
        obj: ta.Any,
        params: ta.Any = None,
        /,
        *,
        ctx: AsQueryContext,
) -> Queryable:
    raise TypeError(obj)


@as_query_.register
def _(
        q: Queryable,
        params: ta.Any = None,
        /,
        *,
        ctx: AsQueryContext,
) -> Queryable:
    if params is not None:
        raise TypeError('Cannot bind params to an already-built Queryable')

    if isinstance(q, Query) and ctx.mode is not None:
        check.arg(q.mode is QueryMode.of(ctx.mode))

    return q


@as_query_.register
def _(
        s: str,
        params: ta.Any = None,
        /,
        *,
        ctx: AsQueryContext,
) -> Queryable:
    return Query(
        mode=QueryMode.of(ctx.mode, QueryMode.QUERY),
        text=s,
        params=_coerce_row_params(params),
    )


##


def as_query_many(
        obj: ta.Any,
        rows: ta.Iterable[ta.Any],
        /,
        *,
        mode: QueryMode | str | None = None,
        adapter: Adapter | None = None,
) -> Query:
    return as_query_many_(
        obj,
        rows,
        ctx=AsQueryContext(
            mode=mode,
            adapter=adapter,
        ),
    )


@functools.singledispatch
def as_query_many_(
        obj: ta.Any,
        rows: ta.Iterable[ta.Any],
        /,
        *,
        ctx: AsQueryContext,
) -> Query:
    raise TypeError(obj)


@as_query_many_.register
def _(
        s: str,
        rows: ta.Iterable[ta.Any],
        /,
        *,
        ctx: AsQueryContext,
) -> Query:
    return Query(
        mode=QueryMode.of(ctx.mode, QueryMode.EXEC),
        text=s,
        params=ManyParams(list(rows)),
    )
