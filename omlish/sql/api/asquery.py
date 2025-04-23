import dataclasses as dc
import functools
import typing as ta

from ... import check
from .base import Querier
from .queries import Query
from .queries import QueryMode


##


@dc.dataclass(frozen=True, kw_only=True)
class AsQueryParams:
    mode: QueryMode | str | None = None
    querier: Querier | None = None


def as_query(
        obj: ta.Any,
        *args: ta.Any,
        mode: QueryMode | str | None = None,
        querier: Querier | None = None,
) -> Query:
    return as_query_(
        obj,
        *args,
        params=AsQueryParams(
            mode=mode,
            querier=querier,
        ),
    )


@functools.singledispatch
def as_query_(
        obj: ta.Any,
        *args: ta.Any,
        params: AsQueryParams,
) -> Query:
    raise TypeError(obj)


@as_query_.register
def _(
        q: Query,
        *,
        params: AsQueryParams,
) -> Query:
    if params.mode is not None:
        check.arg(q.mode is QueryMode.of(params.mode))

    return q


@as_query_.register
def _(
        s: str,
        *args: ta.Any,
        params: AsQueryParams,
) -> Query:
    return Query(
        mode=QueryMode.of(params.mode, QueryMode.QUERY),
        text=s,
        args=args,
    )
