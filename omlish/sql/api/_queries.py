"""
TODO:
 - dialect lol
"""
import collections.abc
import typing as ta

from ... import check
from ..params import ParamStyle
from ..params import UnconsumedParamsError
from ..params import substitute_params
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

    args: list[ta.Any] = []

    if rq.params:
        args.append(substitute_params(rq.params, check.not_none(param_values), strict=True))

    elif param_values:
        raise UnconsumedParamsError(list(param_values))

    return Query(
        mode=QueryMode.of(ctx.mode, QueryMode.QUERY),
        text=rq.s,
        args=args,
    )
