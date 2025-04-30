import typing as ta

from ... import check
from ... import lang
from .asquery import as_query
from .base import Querier
from .base import Rows
from .queries import QueryMode
from .rows import Row


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


def query_first(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> Row:
    with query(querier, obj, *args) as rows:
        return next(rows)


def query_opt_first(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> Row | None:
    with query(querier, obj, *args) as rows:
        return next(rows, None)


def query_one(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> Row:
    with query(querier, obj, *args) as rows:
        return check.single(rows)


def query_opt_one(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> Row | None:
    with query(querier, obj, *args) as rows:
        return check.opt_single(rows)


def query_scalar(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> ta.Any:
    row = query_one(querier, obj, *args)
    return check.single(row.values)


def query_maybe_scalar(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> lang.Maybe[ta.Any]:
    row = query_opt_one(querier, obj, *args)
    if row is not None:
        return lang.just(check.single(row.values))
    else:
        return lang.empty()
