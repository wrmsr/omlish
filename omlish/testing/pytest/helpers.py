import contextlib

import pytest


@contextlib.contextmanager
def assert_raises_star(et):
    num_caught = 0
    try:
        yield
    except* et as eg:  # noqa
        num_caught += 1
    assert num_caught > 0


@pytest.fixture
def asyncio_drainer(event_loop):
    try:
        yield
    finally:
        while event_loop._ready or event_loop._scheduled:  # noqa
            event_loop._run_once()  # noqa
