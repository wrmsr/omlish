import pytest
import trio

from . import sample_kvstore as kvstore
from . import triotp2 as t2


@pytest.fixture
def log_handler():
    import logbook
    handler = logbook.TestHandler(level=logbook.DEBUG)

    with handler.applicationbound():
        yield handler


@pytest.fixture
def mailbox_env():
    t2._mailbox_init()


class GenServerTestState:
    def __init__(self):
        self.ready = trio.Event()
        self.stopped = trio.Event()
        self.info = trio.Event()
        self.casted = trio.Event()

        self.data = {}
        self.did_raise = None
        self.terminated_with = None

        self.info_val = None
        self.unknown_info = []


@pytest.fixture
async def test_state(mailbox_env):
    test_state = GenServerTestState()

    async with trio.open_nursery() as nursery:
        nursery.start_soon(kvstore.start, test_state)

        with trio.fail_after(0.1):
            await test_state.ready.wait()

        yield test_state

        nursery.cancel_scope.cancel()


@pytest.mark.trio
async def test_kvstore_api(test_state):
    val = await kvstore.api.get("foo")
    assert val is None

    val = await kvstore.api.set("foo", "bar")
    assert val is None

    val = await kvstore.api.get("foo")
    assert val == "bar"

    val = await kvstore.api.set("foo", "baz")
    assert val == "bar"

    val = await kvstore.api.get("foo")
    assert val == "baz"

    with pytest.raises(NotImplementedError):
        await kvstore.api.clear()
