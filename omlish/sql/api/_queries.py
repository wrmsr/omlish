"""
TODO:
 - dialect lol - WS-1d routes the full renderer (not just param_style) via the adapter
"""
import collections.abc
import typing as ta

from ... import check
from ... import lang
from ..params import ParamStyle
from ..params import UnconsumedParamsError
from ..params import substitute_params
from ..queries import Stmt
from ..queries.params import Param
from ..queries.rendering import RenderedQuery
from ..queries.rendering import render
from .asquery import AsQueryContext
from .asquery import as_query_
from .asquery import as_query_many_
from .queries import ManyParams
from .queries import NoParams
from .queries import Query
from .queries import Queryable
from .queries import QueryMode
from .queries import QueryParams
from .queries import RowParams


##


def _render_stmt(stmt: Stmt, ctx: AsQueryContext) -> RenderedQuery:
    ps: ParamStyle | None = None
    if ctx.adapter is not None:
        ps = ctx.adapter.param_style

    return render(
        stmt,
        param_style=ps,
    )


def _bind_row(rq: RenderedQuery, param_values: ta.Mapping[Param, ta.Any] | None) -> ta.Any | None:
    if rq.params:
        pvs = lang.merge_dicts(
            param_values or {},
            rq.literals or {},
        )
        return substitute_params(rq.params, pvs, strict=True)

    elif param_values:
        check.none(rq.literals)
        raise UnconsumedParamsError(list(param_values))

    else:
        return None


@as_query_.register
def _(
        stmt: Stmt,
        param_values: ta.Mapping[Param, ta.Any] | None = None,
        /,
        *,
        ctx: AsQueryContext,
) -> Queryable:
    check.isinstance(param_values, (collections.abc.Mapping, None))

    rq = _render_stmt(stmt, ctx)
    bound = _bind_row(rq, param_values)

    params: QueryParams = RowParams(bound) if bound is not None else NoParams()

    return Query(
        mode=QueryMode.of(ctx.mode, QueryMode.QUERY),
        text=rq.s,
        params=params,
    )


@as_query_many_.register
def _(
        stmt: Stmt,
        rows: ta.Iterable[ta.Mapping[Param, ta.Any]],
        /,
        *,
        ctx: AsQueryContext,
) -> Query:
    rq = _render_stmt(stmt, ctx)

    return Query(
        mode=QueryMode.of(ctx.mode, QueryMode.EXEC),
        text=rq.s,
        params=ManyParams([(_bind_row(rq, pv) or ()) for pv in rows]),
    )
