# -*- coding: utf-8 -*-


import asyncio
import logging
import pytest
import testfixtures

from aiotk import (
    cancel,
    PoolClosed,
    TaskPool,
    wait_until_cancelled,
)


@pytest.mark.asyncio
async def test_pool_noop(event_loop):
    """It's safe to do nothing with the pool."""

    async with TaskPool(loop=event_loop):
        pass


@pytest.mark.asyncio
async def test_pool_auto_cancel(event_loop):
    """Lingering tasks are automatically cancelled."""

    ready = asyncio.Event(loop=event_loop)

    async def child_task():
        ready.set()
        await wait_until_cancelled(loop=event_loop)

    async with TaskPool(loop=event_loop) as pool:
        task = await pool.spawn(child_task)
        await ready.wait()
        assert not task.done()

    # The task should have been cancelled.
    assert task.done()
    assert task.cancelled()
    with pytest.raises(asyncio.CancelledError):
        print(task.result())


@pytest.mark.asyncio
async def test_pool_collect(event_loop):
    """Cancelled tasks are collected by the pool."""

    ready = asyncio.Event(loop=event_loop)

    async def child_task():
        ready.set()

    async with TaskPool(loop=event_loop) as pool:
        task = await pool.spawn(child_task)
        await ready.wait()

        # Let the loop complete before we cancel it.
        await pool.wait_idle()

    assert task.done()
    assert not task.cancelled()
    assert task.result() is None


@pytest.mark.asyncio
async def test_pool_collect_cancelled(event_loop):
    """Cancelled tasks are collected by the pool."""

    ready = asyncio.Event(loop=event_loop)

    async def child_task():
        ready.set()
        await wait_until_cancelled(loop=event_loop)

    async with TaskPool(loop=event_loop) as pool:
        task = await pool.spawn(child_task)
        await ready.wait()
        assert not task.done()
        await cancel(task)

        # The task should have been cancelled.
        assert task.done()
        assert task.cancelled()

        # Let the loop complete before we cancel it.
        await pool.wait_idle()


@pytest.mark.asyncio
async def test_pool_collect_crashed(event_loop):
    """Cancelled tasks are collected by the pool."""

    ready = asyncio.Event(loop=event_loop)

    error = Exception('FUUU')

    async def child_task():
        ready.set()
        raise error

    with testfixtures.LogCapture(level=logging.WARNING) as capture:
        async with TaskPool(loop=event_loop) as pool:
            task = await pool.spawn(child_task)
            await ready.wait()

            # Let the loop complete before we cancel it.
            await pool.wait_idle()

    # The task should have crashed.
    assert task.done()
    with pytest.raises(Exception) as exc:
        print(task.result())
    assert exc.value is error

    # Diagnostics should have been logged.
    capture.check(
        ('root', 'ERROR', 'Task crashed!'),
    )


@pytest.mark.asyncio
async def test_pool_spawn_while_waiting(event_loop):
    """Spawning tasks unblocks to update the watch set."""

    done = asyncio.Event(loop=event_loop)

    async def child_task():
        await done.wait()

    async with TaskPool(loop=event_loop) as pool:

        # Spawn a first task.
        await pool.spawn(child_task)

        # Wait until the pool is blocked.
        await pool.wait_busy()

        # Spawn a second task.
        await pool.spawn(child_task)

        # Unblock both tasks and let them finish.
        done.set()
        await pool.wait_idle()


@pytest.mark.asyncio
async def test_pool_spawn_after_close(event_loop):
    """Reject attempts to spawn tasks after the pool is closed."""

    async def child_task():
        pass

    async with TaskPool(loop=event_loop) as pool:
        pass

    with pytest.raises(PoolClosed):
        await pool.spawn(child_task)


@pytest.mark.asyncio
async def test_pool_wait_idle_after_close(event_loop):
    """Reject attempts to wait until idle after the pool is closed."""

    async def child_task():
        pass

    async with TaskPool(loop=event_loop) as pool:
        pass

    with pytest.raises(PoolClosed):
        await pool.wait_idle()


@pytest.mark.asyncio
async def test_pool_wait_busy_after_close(event_loop):
    """Reject attempts to wait until busy after the pool is closed."""

    async def child_task():
        pass

    async with TaskPool(loop=event_loop) as pool:
        pass

    with pytest.raises(PoolClosed):
        await pool.wait_busy()
