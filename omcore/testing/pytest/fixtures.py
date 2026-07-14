import contextlib

import pytest


##


@pytest.fixture
def exit_stack():
    with contextlib.ExitStack() as es:
        yield es


@pytest.fixture
async def async_exit_stack():
    async with contextlib.AsyncExitStack() as aes:
        yield aes
