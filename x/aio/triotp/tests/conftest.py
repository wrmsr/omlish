import pytest

from .. import mailbox, application
import trio

import logbook

from pytest_trio.enable_trio_mode import *  # noqa


@pytest.fixture
def log_handler():
    handler = logbook.TestHandler(level=logbook.DEBUG)

    with handler.applicationbound():
        yield handler


@pytest.fixture
def mailbox_env():
    mailbox._init()
