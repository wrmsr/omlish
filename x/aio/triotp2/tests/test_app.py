import pytest
import trio

from omlish.testing.pytest import assert_raises_star

from .. import triotp2 as t2


class SampleData:
    def __init__(self):
        self.count = 0
        self.stop = trio.Event()


@pytest.fixture
def test_data():
    return SampleData()


class app_a(t2.Module):
    __name__ = 'app_a'

    async def start(self, test_data):
        test_data.count += 1


class app_b(t2.Module):
    __name__ = 'app_b'

    async def start(self, test_data):
        test_data.count += 1
        raise RuntimeError("pytest")


class app_c(t2.Module):
    __name__ = 'app_c'

    async def start(self, test_data):
        test_data.count += 1
        await test_data.stop.wait()


@pytest.mark.trio
async def test_app_stop(test_data, log_handler):
    async with trio.open_nursery() as nursery:
        t2.init_apps(nursery)

        await t2.apps().start(
            t2.AppSpec(
                module=app_c(),
                start_arg=test_data,
                permanent=True,
            )
        )

        await trio.sleep(0.01)
        await t2.apps().stop(app_c.__name__)

    assert test_data.count == 1


@pytest.mark.trio
@pytest.mark.parametrize("max_restarts", [1, 3, 5])
async def test_app_automatic_restart_permanent(test_data, max_restarts, log_handler):
    async with trio.open_nursery() as nursery:
        t2.init_apps(nursery)

        await t2.apps().start(
            t2.AppSpec(
                module=app_a(),
                start_arg=test_data,
                permanent=True,
                opts=t2.SupervisorOptions(
                    max_restarts=max_restarts,
                ),
            )
        )

    assert test_data.count == (max_restarts + 1)
    assert log_handler.has_errors


@pytest.mark.trio
@pytest.mark.parametrize("max_restarts", [1, 3, 5])
async def test_app_automatic_restart_crash(test_data, max_restarts, log_handler):
    with assert_raises_star(RuntimeError):
        async with trio.open_nursery() as nursery:
            t2.init_apps(nursery)

            await t2.apps().start(
                t2.AppSpec(
                    module=app_b(),
                    start_arg=test_data,
                    permanent=False,
                    opts=t2.SupervisorOptions(
                        max_restarts=max_restarts,
                    ),
                )
            )

    assert test_data.count == (max_restarts + 1)
    assert log_handler.has_errors


@pytest.mark.trio
async def test_app_no_automatic_restart(test_data, log_handler):
    async with trio.open_nursery() as nursery:
        t2.init_apps(nursery)

        await t2.apps().start(
            t2.AppSpec(
                module=app_a(),
                start_arg=test_data,
                permanent=False,
            )
        )

    assert test_data.count == 1
    assert not log_handler.has_errors
