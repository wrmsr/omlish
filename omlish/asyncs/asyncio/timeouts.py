# ruff: noqa: UP006 UP007
# @omlish-lite
import asyncio
import typing as ta


AwaitableT = ta.TypeVar('AwaitableT', bound=ta.Awaitable)


def asyncio_maybe_timeout(
        fut: AwaitableT,
        timeout: ta.Optional[float] = None,
) -> AwaitableT:
    if timeout is not None:
        fut = asyncio.wait_for(fut, timeout)  # type: ignore
    return fut
