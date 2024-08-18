# -*- coding: utf-8 -*-


import asyncio
import pytest

from aiotk import cancel, cancel_all, follow_through, wait_until_cancelled
from unittest import mock


@pytest.mark.asyncio
async def test_follow_through_success(event_loop):
    """Child task's return value is returned."""

    async def child_task(result):
        return result

    # Spawn a task that will never complete (unless cancelled).
    task = event_loop.create_task(child_task(123))

    assert not task.done()
    assert (await follow_through(task)) == 123
    assert task.done()
    assert not task.cancelled()


@pytest.mark.asyncio
async def test_follow_through_failure(event_loop):
    """Child task's exception is propagated."""

    async def child_task(error):
        raise error

    # Spawn a task that will never complete (unless cancelled).
    error = Exception()
    task = event_loop.create_task(child_task(error))

    assert not task.done()
    with pytest.raises(Exception) as exc:
        print(await follow_through(task))
    assert exc.value is error
    assert task.done()
    assert not task.cancelled()


@pytest.mark.asyncio
async def test_follow_through_forward_cancel(event_loop):
    """Cancellation is propagated to the child task."""

    task = mock.MagicMock()
    task.cancel.side_effect = [True]

    with mock.patch('asyncio.wait') as wait:
        error = asyncio.CancelledError()
        success = asyncio.Future(loop=event_loop)
        success.set_result(None)
        wait.side_effect = [
            error,
            success,
        ]
        with pytest.raises(asyncio.CancelledError) as exc:
            await follow_through(task)
        assert exc.value is error

    wait.assert_called_with({task}, loop=event_loop)
    assert wait.call_count == 2
    task.result.assert_not_called
    task.cancel.assert_called_once_with()


@pytest.mark.asyncio
async def test_cancel_success(event_loop):
    """Child task's CancelledError exception is not propagated."""

    async def child_task(future):
        await future

    # Spawn a task that will never complete (unless cancelled).
    future = asyncio.Future(loop=event_loop)
    task = event_loop.create_task(child_task(future))

    # Cancel the task.
    assert not task.done()
    await cancel(task)
    assert task.done()
    assert task.cancelled()

    # Ensure that it was cancelled.
    with pytest.raises(asyncio.CancelledError):
        print(await task)


@pytest.mark.asyncio
async def test_cancel_despite_cancel(event_loop):
    """CancelledError exception is not propagated until the task completes."""

    task = mock.MagicMock()
    task.cancel.side_effect = [True]

    with mock.patch('asyncio.wait') as wait:
        error = asyncio.CancelledError()
        success = asyncio.Future(loop=event_loop)
        success.set_result(None)
        wait.side_effect = [
            error,
            success,
        ]
        with pytest.raises(asyncio.CancelledError) as exc:
            await cancel(task)
        assert exc.value is error

    wait.assert_called_with({task}, loop=event_loop)
    assert wait.call_count == 2
    task.cancel.assert_called_once_with()


@pytest.mark.asyncio
async def test_cancel_already_done(event_loop):
    """No-op on task that has already completed."""

    async def child_task(future):
        pass

    # Spawn a task that will complete immediately.
    future = asyncio.Future(loop=event_loop)
    task = event_loop.create_task(child_task(future))

    await task
    assert task.done()

    await cancel(task)


@pytest.mark.asyncio
async def test_cancel_all_success(event_loop):
    """Child task's CancelledError exceptions are not propagated."""

    async def child_task(future):
        await future

    # Spawn a task that will never complete (unless cancelled).
    future = asyncio.Future(loop=event_loop)
    children = {
        event_loop.create_task(child_task(future)) for i in range(5)
    }

    # Cancel the task.
    assert not any(task.done() for task in children)
    await cancel_all(children)
    assert all(task.done() for task in children)
    assert all(task.cancelled() for task in children)

    # Ensure that it was cancelled.
    for task in children:
        with pytest.raises(asyncio.CancelledError):
            print(await task)


@pytest.mark.asyncio
async def test_cancel_all_despite_cancel(event_loop):
    """CancelledError exception is not propagated until all tasks complete."""

    tasks = set()
    for _ in range(5):
        task = mock.MagicMock()
        task.cancel.side_effect = [True]
        tasks.add(task)

    with mock.patch('asyncio.wait') as wait:
        error = asyncio.CancelledError()
        success = asyncio.Future(loop=event_loop)
        success.set_result(None)
        wait.side_effect = [
            error,
            success,
        ]
        with pytest.raises(asyncio.CancelledError) as exc:
            await cancel_all(tasks)
        assert exc.value is error

    assert wait.call_args_list == [
        mock.call(tasks, loop=event_loop),
        mock.call(tasks, loop=event_loop),
    ]
    assert wait.call_count == 2
    for task in tasks:
        task.cancel.assert_called_once_with()


@pytest.mark.asyncio
async def test_wait_until_cancelled_propagate(event_loop):
    """CancelledError exception is propagated by default."""

    child_ready = asyncio.Event(loop=event_loop)

    async def child_task():
        child_ready.set()
        await wait_until_cancelled(loop=event_loop)

    task = event_loop.create_task(child_task())
    await child_ready.wait()

    assert not task.done()
    await cancel(task)
    assert task.done()
    assert task.cancelled()
    with pytest.raises(asyncio.CancelledError):
        print(task.result())


@pytest.mark.asyncio
async def test_wait_until_cancelled_silence(event_loop):
    """CancelledError exception can be silenced."""

    child_ready = asyncio.Event(loop=event_loop)

    async def child_task():
        child_ready.set()
        await wait_until_cancelled(propagate=False, loop=event_loop)

    task = event_loop.create_task(child_task())
    await child_ready.wait()

    assert not task.done()
    await cancel(task)
    assert task.done()
    assert not task.cancelled()
    assert task.result() is None
