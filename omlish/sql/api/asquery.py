import functools
import typing as ta

from ... import check
from ... import dataclasses as dc
from .adapters import Adapter
from .queries import Query
from .queries import QueryMode


##


@dc.dataclass(frozen=True, kw_only=True)
class AsQueryContext:
    mode: QueryMode | str | None = None
    adapter: Adapter | None = None


def as_query(
        obj: ta.Any,
        /,
        *args: ta.Any,
        mode: QueryMode | str | None = None,
        adapter: Adapter | None = None,
) -> Query:
    return as_query_(
        obj,
        *args,
        ctx=AsQueryContext(
            mode=mode,
            adapter=adapter,
        ),
    )


@functools.singledispatch
def as_query_(
        obj: ta.Any,
        /,
        *args: ta.Any,
        ctx: AsQueryContext,
) -> Query:
    raise TypeError(obj)


@as_query_.register
def _(
        q: Query,
        /,
        *,
        ctx: AsQueryContext,
) -> Query:
    if ctx.mode is not None:
        check.arg(q.mode is QueryMode.of(ctx.mode))

    return q


@as_query_.register
def _(
        s: str,
        /,
        *args: ta.Any,
        ctx: AsQueryContext,
) -> Query:
    return Query(
        mode=QueryMode.of(ctx.mode, QueryMode.QUERY),
        text=s,
        args=args,
    )
