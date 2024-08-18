# -*- coding: utf-8 -*-


import asyncio
import logging
import pytest
import testfixtures

from aiotk import PeriodicTask
from unittest import mock


def make_success(result, loop):
    f = asyncio.Future(loop=loop)
    f.set_result(result)
    return f


@pytest.mark.asyncio
async def test_periodic_task(event_loop):
    """The background task repeats until we leave the context manager."""

    sem = asyncio.Semaphore(0, loop=event_loop)

    async def task():
        sem.release()

    with mock.patch('asyncio.sleep') as sleep:
        sleep.side_effect = [
            make_success(None, loop=event_loop),
            make_success(None, loop=event_loop),
            make_success(None, loop=event_loop),
            asyncio.Future(loop=event_loop),
        ]
        async with PeriodicTask(task, 0.01, loop=event_loop):
            await sem.acquire()
            await sem.acquire()
            await sem.acquire()

    assert sleep.call_args_list == [
        mock.call(0.01),
        mock.call(0.01),
        mock.call(0.01),
        mock.call(0.01),
    ]


@pytest.mark.asyncio
async def test_periodic_task_cancelled_while_task_is_running(event_loop):
    """The background task is cancelled."""

    ready = asyncio.Event(loop=event_loop)
    close = asyncio.Event(loop=event_loop)

    async def task():
        ready.set()
        await close.wait()

    with mock.patch('asyncio.sleep') as sleep:
        sleep.return_value = None
        async with PeriodicTask(task, 0.01, loop=event_loop):
            await ready.wait()

    assert sleep.call_args_list == []


@pytest.mark.asyncio
async def test_periodic_task_respawn_after_crash(event_loop):
    """Background task repeats despite exceptions (which are logged)."""

    sem = asyncio.Semaphore(0, loop=event_loop)

    async def task():
        sem.release()
        raise Exception('Crash this task!')

    with mock.patch('asyncio.sleep') as sleep:
        sleep.side_effect = [
            make_success(None, loop=event_loop),
            make_success(None, loop=event_loop),
            make_success(None, loop=event_loop),
            asyncio.Future(loop=event_loop),
        ]
        with testfixtures.LogCapture(level=logging.WARNING) as logs:
            async with PeriodicTask(task, 0.01, loop=event_loop):
                await sem.acquire()
                await sem.acquire()
                await sem.acquire()

    assert sleep.call_args_list == [
        mock.call(0.01),
        mock.call(0.01),
        mock.call(0.01),
        mock.call(0.01),
    ]

    logs.check(
        ('root', 'ERROR', 'Executing periodic task.'),
        ('root', 'ERROR', 'Executing periodic task.'),
        ('root', 'ERROR', 'Executing periodic task.'),
        ('root', 'ERROR', 'Executing periodic task.'),
    )
