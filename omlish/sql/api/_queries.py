"""
TODO:
 - dialect lol
"""
from ..queries import Stmt
from ..queries.rendering import render
from .funcs import as_query
from .queries import Query
from .queries import QueryMode


##


@as_query.register
def _(
        stmt: Stmt,
        *,
        mode: QueryMode | str | None = None,
) -> Query:
    rq = render(stmt)

    # FIXME: rq.args
    return Query(
        mode=QueryMode.of(mode, QueryMode.QUERY),
        text=rq.s,
        args=[],
    )
