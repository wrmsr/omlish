import pytest
import trio

from omlish.testing.pytest import assert_raises_star

from .. import triotp2 as t2


class SampleData:
    def __init__(self):
        self.exec_count = 0


async def sample_task(test_data):
    test_data.exec_count += 1


async def sample_task_error(test_data):
    test_data.exec_count += 1
    raise RuntimeError('pytest')


@pytest.mark.trio
@pytest.mark.parametrize('max_restarts', [1, 3, 5])
async def test_automatic_restart_permanent(max_restarts, log_handler):
    test_data = SampleData()

    async with trio.open_nursery() as nursery:
        children = [
            t2.ChildSpec(
                id='sample_task',
                task=sample_task,
                args=[test_data],
                restart=t2.RestartStrategy.PERMANENT,
            ),
        ]
        opts = t2.SupervisorOptions(
            max_restarts=max_restarts,
            max_seconds=5,
        )
        await nursery.start(t2.supervisor_start, children, opts)

    assert test_data.exec_count == (max_restarts + 1)
    assert log_handler.has_errors


@pytest.mark.trio
@pytest.mark.parametrize('max_restarts', [1, 3, 5])
@pytest.mark.parametrize(
    'strategy',
    [
        t2.RestartStrategy.PERMANENT,
        t2.RestartStrategy.TRANSIENT,
    ],
)
async def test_automatic_restart_crash(max_restarts, strategy, log_handler):
    test_data = SampleData()

    with assert_raises_star(RuntimeError):
        async with trio.open_nursery() as nursery:
            children = [
                t2.ChildSpec(
                    id='sample_task',
                    task=sample_task_error,
                    args=[test_data],
                    restart=strategy,
                ),
            ]
            opts = t2.SupervisorOptions(
                max_restarts=max_restarts,
                max_seconds=5,
            )
            await nursery.start(t2.supervisor_start, children, opts)

    assert test_data.exec_count == (max_restarts + 1)
    assert log_handler.has_errors


@pytest.mark.trio
@pytest.mark.parametrize(
    'strategy',
    [
        t2.RestartStrategy.TEMPORARY,
        t2.RestartStrategy.TRANSIENT,
    ],
)
async def test_no_restart(strategy, log_handler):
    test_data = SampleData()

    async with trio.open_nursery() as nursery:
        children = [
            t2.ChildSpec(
                id='sample_task',
                task=sample_task,
                args=[test_data],
                restart=strategy,
            ),
        ]
        opts = t2.SupervisorOptions(
            max_restarts=3,
            max_seconds=5,
        )
        await nursery.start(t2.supervisor_start, children, opts)

    assert test_data.exec_count == 1
    assert not log_handler.has_errors
