import typing as ta

from .base import Querier
from .base import Rows
from .queries import Query
from .queries import QueryMode
from .queries import as_query
from .rows import Row


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
    q = as_query(obj, *args, mode=QueryMode.QUERY)

    return querier.query(q)


#


def query_all(
        querier: Querier,
        *args: ta.Any,
) -> list[Row]:
    with query(querier, *args) as rows:
        return list(rows)


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
    q = as_query(obj, *args, mode=QueryMode.EXEC)

    with querier.query(q):
        pass
