"""
TODO:
 - dialect lol
 - args lol
"""
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
    rq = render(stmt)

    if rq.args:
        raise NotImplementedError

    return Query(
        mode=QueryMode.of(params.mode, QueryMode.QUERY),
        text=rq.s,
        args=[],
    )
