# -*- coding: utf-8 -*-


import asyncio
import pytest

from aiotk import EnsureDone, wait_until_cancelled


@pytest.mark.asyncio
async def test_ensure_done_cancel(event_loop):
    """By default, the background task is cancelled when leaving the scope."""

    async def child_task():
        await wait_until_cancelled(loop=event_loop)

    async with EnsureDone(child_task(), loop=event_loop) as task:
        assert not task.done()

    assert task.done()
    assert task.cancelled()
    with pytest.raises(asyncio.CancelledError):
        print(task.result())


@pytest.mark.asyncio
async def test_ensure_done_success(event_loop):
    """The background task can be scheduled to gracefully shutdown."""

    ready = asyncio.Event(loop=event_loop)

    async def child_task():
        await ready.wait()

    async with EnsureDone(child_task(), cancel=False, loop=event_loop) as task:
        assert not task.done()
        ready.set()

    assert task.done()
    assert not task.cancelled()
    assert task.result() is None
