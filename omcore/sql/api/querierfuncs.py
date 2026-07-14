import typing as ta

from ... import check
from ... import lang
from .asquery import as_query
from .asquery import as_query_many
from .core import AsyncRows
from .core import Rows
from .queriers import AsyncQuerier
from .queriers import Querier
from .queries import QueryMode
from .rows import Row


##


def _sync_async_query_func(sync_fn, async_fn):
    def outer(fn):  # noqa
        def inner(querier, *args, **kwargs):
            if isinstance(querier, AsyncQuerier):
                return async_fn(querier, *args, **kwargs)

            elif isinstance(querier, Querier):
                return sync_fn(querier, *args, **kwargs)

            else:
                raise TypeError(querier)

        return inner

    return outer


##


def sync_exec(  # noqa
        querier: Querier,
        obj: ta.Any,
        params: ta.Any = None,
) -> None:
    q = as_query(
        obj,
        params,
        mode=QueryMode.EXEC,
        adapter=querier.adapter,
    )

    with querier.query(q):
        pass


async def async_exec(  # noqa
        querier: AsyncQuerier,
        obj: ta.Any,
        params: ta.Any = None,
) -> None:
    q = as_query(
        obj,
        params,
        mode=QueryMode.EXEC,
        adapter=querier.adapter,
    )

    async with querier.query(q):
        pass


@ta.overload
def exec(  # noqa
        querier: Querier,
        obj: ta.Any,
        params: ta.Any = None,
) -> None:
    ...


@ta.overload
def exec(  # noqa
        querier: AsyncQuerier,
        obj: ta.Any,
        params: ta.Any = None,
) -> ta.Awaitable[None]:
    ...


@_sync_async_query_func(sync_exec, async_exec)
def exec(*args, **kwargs):  # noqa
    raise RuntimeError


##


def sync_exec_many(
        querier: Querier,
        obj: ta.Any,
        rows: ta.Iterable[ta.Any],
) -> None:
    q = as_query_many(
        obj,
        rows,
        mode=QueryMode.EXEC,
        adapter=querier.adapter,
    )

    with querier.query(q):
        pass


async def async_exec_many(
        querier: AsyncQuerier,
        obj: ta.Any,
        rows: ta.Iterable[ta.Any],
) -> None:
    q = as_query_many(
        obj,
        rows,
        mode=QueryMode.EXEC,
        adapter=querier.adapter,
    )

    async with querier.query(q):
        pass


@ta.overload
def exec_many(
        querier: Querier,
        obj: ta.Any,
        rows: ta.Iterable[ta.Any],
) -> None:
    ...


@ta.overload
def exec_many(
        querier: AsyncQuerier,
        obj: ta.Any,
        rows: ta.Iterable[ta.Any],
) -> ta.Awaitable[None]:
    ...


@_sync_async_query_func(sync_exec_many, async_exec_many)
def exec_many(*args, **kwargs):
    raise RuntimeError


##


def sync_query(
        querier: Querier,
        obj: ta.Any,
        params: ta.Any = None,
) -> ta.ContextManager[Rows]:
    q = as_query(
        obj,
        params,
        mode=QueryMode.QUERY,
        adapter=querier.adapter,
    )

    return querier.query(q)


def async_query(
        querier: AsyncQuerier,
        obj: ta.Any,
        params: ta.Any = None,
) -> ta.AsyncContextManager[AsyncRows]:
    q = as_query(
        obj,
        params,
        mode=QueryMode.QUERY,
        adapter=querier.adapter,
    )

    return querier.query(q)


@ta.overload
def query(
        querier: Querier,
        obj: ta.Any,
        params: ta.Any = None,
) -> ta.ContextManager[Rows]:
    ...


@ta.overload
def query(
        querier: AsyncQuerier,
        obj: ta.Any,
        params: ta.Any = None,
) -> ta.AsyncContextManager[AsyncRows]:
    ...


@_sync_async_query_func(sync_query, async_query)
def query(*args, **kwargs):
    raise RuntimeError


##


def sync_query_all(
        querier: Querier,
        obj: ta.Any,
        params: ta.Any = None,
) -> list[Row]:
    with sync_query(querier, obj, params) as rows:
        return list(rows)


async def async_query_all(
        querier: AsyncQuerier,
        obj: ta.Any,
        params: ta.Any = None,
) -> list[Row]:
    async with async_query(querier, obj, params) as rows:
        return await lang.async_list(rows)


@ta.overload
def query_all(
        querier: Querier,
        obj: ta.Any,
        params: ta.Any = None,
) -> list[Row]:
    ...


@ta.overload
def query_all(
        querier: AsyncQuerier,
        obj: ta.Any,
        params: ta.Any = None,
) -> ta.Awaitable[list[Row]]:
    ...


@_sync_async_query_func(sync_query_all, async_query_all)
def query_all(*args, **kwargs):
    raise RuntimeError


#


def sync_query_first(
        querier: Querier,
        obj: ta.Any,
        params: ta.Any = None,
) -> Row:
    with sync_query(querier, obj, params) as rows:
        return next(rows)


async def async_query_first(
        querier: AsyncQuerier,
        obj: ta.Any,
        params: ta.Any = None,
) -> Row:
    async with async_query(querier, obj, params) as rows:
        return await anext(rows)


@ta.overload
def query_first(
        querier: Querier,
        obj: ta.Any,
        params: ta.Any = None,
) -> Row:
    ...


@ta.overload
def query_first(
        querier: AsyncQuerier,
        obj: ta.Any,
        params: ta.Any = None,
) -> ta.Awaitable[Row]:
    ...


@_sync_async_query_func(sync_query_first, async_query_first)
def query_first(*args, **kwargs):
    raise RuntimeError


##


def sync_query_opt_first(
        querier: Querier,
        obj: ta.Any,
        params: ta.Any = None,
) -> Row | None:
    with sync_query(querier, obj, params) as rows:
        return next(rows, None)


async def async_query_opt_first(
        querier: AsyncQuerier,
        obj: ta.Any,
        params: ta.Any = None,
) -> Row | None:
    async with async_query(querier, obj, params) as rows:
        return await anext(rows, None)


@ta.overload
def query_opt_first(
        querier: Querier,
        obj: ta.Any,
        params: ta.Any = None,
) -> Row | None:
    ...


@ta.overload
def query_opt_first(
        querier: AsyncQuerier,
        obj: ta.Any,
        params: ta.Any = None,
) -> ta.Awaitable[Row | None]:
    ...


@_sync_async_query_func(sync_query_opt_first, async_query_opt_first)
def query_opt_first(*args, **kwargs):
    raise RuntimeError


##


def sync_query_one(
        querier: Querier,
        obj: ta.Any,
        params: ta.Any = None,
) -> Row:
    with sync_query(querier, obj, params) as rows:
        return check.single(rows)


async def async_query_one(
        querier: AsyncQuerier,
        obj: ta.Any,
        params: ta.Any = None,
) -> Row:
    async with async_query(querier, obj, params) as rows:
        return await check.async_single(rows)


@ta.overload
def query_one(
        querier: Querier,
        obj: ta.Any,
        params: ta.Any = None,
) -> Row:
    ...


@ta.overload
def query_one(
        querier: AsyncQuerier,
        obj: ta.Any,
        params: ta.Any = None,
) -> ta.Awaitable[Row]:
    ...


@_sync_async_query_func(sync_query_one, async_query_one)
def query_one(*args, **kwargs):
    raise RuntimeError


##


def sync_query_opt_one(
        querier: Querier,
        obj: ta.Any,
        params: ta.Any = None,
) -> Row | None:
    with sync_query(querier, obj, params) as rows:
        return check.opt_single(rows)


async def async_query_opt_one(
        querier: AsyncQuerier,
        obj: ta.Any,
        params: ta.Any = None,
) -> Row | None:
    async with async_query(querier, obj, params) as rows:
        return await check.async_opt_single(rows)


@ta.overload
def query_opt_one(
        querier: Querier,
        obj: ta.Any,
        params: ta.Any = None,
) -> Row | None:
    ...


@ta.overload
def query_opt_one(
        querier: AsyncQuerier,
        obj: ta.Any,
        params: ta.Any = None,
) -> ta.Awaitable[Row | None]:
    ...


@_sync_async_query_func(sync_query_opt_one, async_query_opt_one)
def query_opt_one(*args, **kwargs):
    raise RuntimeError


##


def sync_query_scalar(
        querier: Querier,
        obj: ta.Any,
        params: ta.Any = None,
) -> ta.Any:
    row = sync_query_one(querier, obj, params)
    return check.single(row.values)


async def async_query_scalar(
        querier: AsyncQuerier,
        obj: ta.Any,
        params: ta.Any = None,
) -> ta.Any:
    row = await async_query_one(querier, obj, params)
    return check.single(row.values)


@ta.overload
def query_scalar(
        querier: Querier,
        obj: ta.Any,
        params: ta.Any = None,
) -> ta.Any:
    ...


@ta.overload
def query_scalar(
        querier: AsyncQuerier,
        obj: ta.Any,
        params: ta.Any = None,
) -> ta.Awaitable[ta.Any]:
    ...


@_sync_async_query_func(sync_query_scalar, async_query_scalar)
def query_scalar(*args, **kwargs):
    raise RuntimeError


##


def sync_query_maybe_scalar(
        querier: Querier,
        obj: ta.Any,
        params: ta.Any = None,
) -> lang.Maybe[ta.Any]:
    row = sync_query_opt_one(querier, obj, params)
    if row is not None:
        return lang.just(check.single(row.values))
    else:
        return lang.empty()


async def async_query_maybe_scalar(
        querier: AsyncQuerier,
        obj: ta.Any,
        params: ta.Any = None,
) -> lang.Maybe[ta.Any]:
    row = await async_query_opt_one(querier, obj, params)
    if row is not None:
        return lang.just(check.single(row.values))
    else:
        return lang.empty()


@ta.overload
def query_maybe_scalar(
        querier: Querier,
        obj: ta.Any,
        params: ta.Any = None,
) -> lang.Maybe[ta.Any]:
    ...


@ta.overload
def query_maybe_scalar(
        querier: AsyncQuerier,
        obj: ta.Any,
        params: ta.Any = None,
) -> ta.Awaitable[lang.Maybe[ta.Any]]:
    ...


@_sync_async_query_func(sync_query_maybe_scalar, async_query_maybe_scalar)
def query_maybe_scalar(*args, **kwargs):
    raise RuntimeError
