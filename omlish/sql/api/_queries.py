"""
TODO:
 - dialect lol
 - args lol
"""
from ..params import ParamStyle
from ..queries import Stmt
from ..queries.rendering import render
from .asquery import AsQueryParams
from .asquery import as_query_
from .queries import Query
from .queries import QueryMode


##


@as_query_.register
def _(
        stmt: Stmt,
        *,
        params: AsQueryParams,
) -> Query:
    ps: ParamStyle | None = None
    if params.adapter is not None:
        ps = params.adapter.param_style

    rq = render(
        stmt,
        param_style=ps,
    )

    if rq.params:
        raise NotImplementedError

    return Query(
        mode=QueryMode.of(params.mode, QueryMode.QUERY),
        text=rq.s,
        args=[],
    )
