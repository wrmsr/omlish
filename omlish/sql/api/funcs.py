import typing as ta

from .base import Querier
from .base import Rows
from .queries import Query
from .queries import QueryMode


##


@ta.overload
def query(
        querier: Querier,
        query: Query,  # noqa
) -> Rows:
    ...


@ta.overload
def query(
        querier: Querier,
        text: str,
        *args: ta.Any,
) -> Rows:
    ...


def query(
        querier,
        obj,
        *args,
):
    if isinstance(obj, Query):
        q = obj
    else:
        q = Query.of(obj, *args, mode=QueryMode.QUERY)

    return querier.query(q)


##


@ta.overload
def exec(  # noqa
        querier: Querier,
        query: Query,  # noqa
) -> None:
    ...


@ta.overload
def exec(  # noqa
        querier: Querier,
        text: str,
        *args: ta.Any,
) -> None:
    ...


def exec(  # noqa
    querier,
    obj,
    *args,
):
    if isinstance(obj, Query):
        q = obj
    else:
        q = Query.of(obj, *args, mode=QueryMode.EXEC)

    with querier.query(q):
        pass
