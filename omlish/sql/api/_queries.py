"""
TODO:
 - dialect lol
 - args lol
"""
import collections.abc
import typing as ta

from ... import check
from ..params import ParamStyle
from ..queries import Stmt
from ..queries.params import Param
from ..queries.rendering import render
from .asquery import AsQueryContext
from .asquery import as_query_
from .queries import Query
from .queries import QueryMode


##


@as_query_.register
def _(
        stmt: Stmt,
        param_values: ta.Mapping[Param, ta.Any] | None = None,
        /,
        *,
        ctx: AsQueryContext,
) -> Query:
    check.isinstance(param_values, (collections.abc.Mapping, None))

    ps: ParamStyle | None = None
    if ctx.adapter is not None:
        ps = ctx.adapter.param_style

    rq = render(
        stmt,
        param_style=ps,
    )

    if rq.params:
        raise NotImplementedError

    else:
        check.arg(not param_values)

    return Query(
        mode=QueryMode.of(ctx.mode, QueryMode.QUERY),
        text=rq.s,
        args=[],
    )
