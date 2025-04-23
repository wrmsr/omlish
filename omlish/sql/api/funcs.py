import typing as ta

from .asquery import as_query
from .base import Querier
from .base import Rows
from .queries import QueryMode
from .rows import Row


##


def query(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> Rows:
    q = as_query(
        obj,
        *args,
        mode=QueryMode.QUERY,
        querier=querier,
    )

    return querier.query(q)


#


def query_all(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> list[Row]:
    with query(querier, obj, *args) as rows:
        return list(rows)


##


def exec(  # noqa
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> None:
    q = as_query(
        obj,
        *args,
        mode=QueryMode.EXEC,
        querier=querier,
    )

    with querier.query(q):
        pass
