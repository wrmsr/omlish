import typing as ta

from ... import check
from ... import lang
from .asquery import as_query
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
        *args: ta.Any,
) -> None:
    q = as_query(
        obj,
        *args,
        mode=QueryMode.EXEC,
        adapter=querier.adapter,
    )

    with querier.query(q):
        pass


async def async_exec(  # noqa
        querier: AsyncQuerier,
        obj: ta.Any,
        *args: ta.Any,
) -> None:
    q = as_query(
        obj,
        *args,
        mode=QueryMode.EXEC,
        adapter=querier.adapter,
    )

    async with querier.query(q):
        pass


@ta.overload
def exec(  # noqa
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> None:
    ...


@ta.overload
def exec(  # noqa
        querier: AsyncQuerier,
        obj: ta.Any,
        *args: ta.Any,
) -> ta.Awaitable[None]:
    ...


@_sync_async_query_func(sync_exec, async_exec)
def exec(*args, **kwargs):  # noqa
    raise RuntimeError


##


def sync_query(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> ta.ContextManager['Rows']:
    q = as_query(
        obj,
        *args,
        mode=QueryMode.QUERY,
        adapter=querier.adapter,
    )

    return querier.query(q)


def async_query(
        querier: AsyncQuerier,
        obj: ta.Any,
        *args: ta.Any,
) -> ta.AsyncContextManager['AsyncRows']:
    q = as_query(
        obj,
        *args,
        mode=QueryMode.QUERY,
        adapter=querier.adapter,
    )

    return querier.query(q)


@ta.overload
def query(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> ta.ContextManager['Rows']:
    ...


@ta.overload
def query(
        querier: AsyncQuerier,
        obj: ta.Any,
        *args: ta.Any,
) -> ta.AsyncContextManager['Rows']:
    ...


@_sync_async_query_func(sync_query, async_query)
def query(*args, **kwargs):
    raise RuntimeError


##


def sync_query_all(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> list[Row]:
    with sync_query(querier, obj, *args) as rows:
        return list(rows)


async def async_query_all(
        querier: AsyncQuerier,
        obj: ta.Any,
        *args: ta.Any,
) -> list[Row]:
    async with async_query(querier, obj, *args) as rows:
        return await lang.async_list(rows)


@ta.overload
def query_all(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> list[Row]:
    ...


@ta.overload
def query_all(
        querier: AsyncQuerier,
        obj: ta.Any,
        *args: ta.Any,
) -> ta.Awaitable[list[Row]]:
    ...


@_sync_async_query_func(sync_query_all, async_query_all)
def query_all(*args, **kwargs):
    raise RuntimeError


#


def sync_query_first(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> Row:
    with sync_query(querier, obj, *args) as rows:
        return next(rows)


async def async_query_first(
        querier: AsyncQuerier,
        obj: ta.Any,
        *args: ta.Any,
) -> Row:
    async with async_query(querier, obj, *args) as rows:
        return await anext(rows)


@ta.overload
def query_first(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> Row:
    ...


@ta.overload
def query_first(
        querier: AsyncQuerier,
        obj: ta.Any,
        *args: ta.Any,
) -> ta.Awaitable[Row]:
    ...


@_sync_async_query_func(sync_query_first, async_query_first)
def query_first(*args, **kwargs):
    raise RuntimeError


##


def sync_query_opt_first(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> Row | None:
    with sync_query(querier, obj, *args) as rows:
        return next(rows, None)


async def async_query_opt_first(
        querier: AsyncQuerier,
        obj: ta.Any,
        *args: ta.Any,
) -> Row | None:
    async with async_query(querier, obj, *args) as rows:
        return await anext(rows, None)


@ta.overload
def query_opt_first(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> Row | None:
    ...


@ta.overload
def query_opt_first(
        querier: AsyncQuerier,
        obj: ta.Any,
        *args: ta.Any,
) -> ta.Awaitable[Row | None]:
    ...


@_sync_async_query_func(sync_query_opt_first, async_query_opt_first)
def query_opt_first(*args, **kwargs):
    raise RuntimeError


##


def sync_query_one(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> Row:
    with sync_query(querier, obj, *args) as rows:
        return check.single(rows)


async def async_query_one(
        querier: AsyncQuerier,
        obj: ta.Any,
        *args: ta.Any,
) -> Row:
    async with async_query(querier, obj, *args) as rows:
        return await check.async_single(rows)


@ta.overload
def query_one(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> Row:
    ...


@ta.overload
def query_one(
        querier: AsyncQuerier,
        obj: ta.Any,
        *args: ta.Any,
) -> ta.Awaitable[Row]:
    ...


@_sync_async_query_func(sync_query_one, async_query_one)
def query_one(*args, **kwargs):
    raise RuntimeError


##


def sync_query_opt_one(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> Row | None:
    with sync_query(querier, obj, *args) as rows:
        return check.opt_single(rows)


async def async_query_opt_one(
        querier: AsyncQuerier,
        obj: ta.Any,
        *args: ta.Any,
) -> Row | None:
    async with async_query(querier, obj, *args) as rows:
        return await check.async_opt_single(rows)


@ta.overload
def query_opt_one(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> Row | None:
    ...


@ta.overload
def query_opt_one(
        querier: AsyncQuerier,
        obj: ta.Any,
        *args: ta.Any,
) -> ta.Awaitable[Row | None]:
    ...


@_sync_async_query_func(sync_query_opt_one, async_query_opt_one)
def query_opt_one(*args, **kwargs):
    raise RuntimeError


##


def sync_query_scalar(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> ta.Any:
    row = sync_query_one(querier, obj, *args)
    return check.single(row.values)


async def async_query_scalar(
        querier: AsyncQuerier,
        obj: ta.Any,
        *args: ta.Any,
) -> ta.Any:
    row = await async_query_one(querier, obj, *args)
    return check.single(row.values)


@ta.overload
def query_scalar(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> ta.Any:
    ...


@ta.overload
def query_scalar(
        querier: AsyncQuerier,
        obj: ta.Any,
        *args: ta.Any,
) -> ta.Awaitable[ta.Any]:
    ...


@_sync_async_query_func(sync_query_scalar, async_query_scalar)
def query_scalar(*args, **kwargs):
    raise RuntimeError


##


def sync_query_maybe_scalar(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> lang.Maybe[ta.Any]:
    row = sync_query_opt_one(querier, obj, *args)
    if row is not None:
        return lang.just(check.single(row.values))
    else:
        return lang.empty()


async def async_query_maybe_scalar(
        querier: AsyncQuerier,
        obj: ta.Any,
        *args: ta.Any,
) -> lang.Maybe[ta.Any]:
    row = await async_query_opt_one(querier, obj, *args)
    if row is not None:
        return lang.just(check.single(row.values))
    else:
        return lang.empty()


@ta.overload
def query_maybe_scalar(
        querier: Querier,
        obj: ta.Any,
        *args: ta.Any,
) -> lang.Maybe[ta.Any]:
    ...


@ta.overload
def query_maybe_scalar(
        querier: AsyncQuerier,
        obj: ta.Any,
        *args: ta.Any,
) -> ta.Awaitable[lang.Maybe[ta.Any]]:
    ...


@_sync_async_query_func(sync_query_maybe_scalar, async_query_maybe_scalar)
def query_maybe_scalar(*args, **kwargs):
    raise RuntimeError
