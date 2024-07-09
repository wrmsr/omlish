import pytest

from .. import triotp2 as t2


@pytest.fixture
def log_handler():
    import logbook
    handler = logbook.TestHandler(level=logbook.DEBUG)

    with handler.applicationbound():
        yield handler


@pytest.fixture
def mailbox_env():
    t2.init_mailboxes()


