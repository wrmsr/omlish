import pytest
import trio

from . import sample_kvstore
from .. import triotp2 as t2


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


@pytest.fixture(scope='function')
def kvstore() -> sample_kvstore.KvStore:
    return sample_kvstore.KvStore()


@pytest.fixture
async def test_state(kvstore, mailbox_env):
    test_state = GenServerTestState()

    async with trio.open_nursery() as nursery:
        nursery.start_soon(kvstore.start, test_state)

        with trio.fail_after(0.1):
            await test_state.ready.wait()

        yield test_state

        nursery.cancel_scope.cancel()


@pytest.mark.trio
async def test_kvstore_api(test_state):
    val = await sample_kvstore.api.get('foo')
    assert val is None

    val = await sample_kvstore.api.set('foo', 'bar')
    assert val is None

    val = await sample_kvstore.api.get('foo')
    assert val == 'bar'

    val = await sample_kvstore.api.set('foo', 'baz')
    assert val == 'bar'

    val = await sample_kvstore.api.get('foo')
    assert val == 'baz'

    with pytest.raises(NotImplementedError):
        await sample_kvstore.api.clear()


@pytest.mark.trio
async def test_kvstore_call_delayed(test_state):
    async with trio.open_nursery() as nursery:
        resp = await sample_kvstore.special_call.delayed(nursery)

    assert resp == 'done'


@pytest.mark.trio
async def test_kvstore_call_timeout(test_state):
    with pytest.raises(trio.TooSlowError):
        await sample_kvstore.special_call.timed_out(0.01)


@pytest.mark.trio
async def test_kvstore_call_stopped(test_state):
    with pytest.raises(t2.GenServerExited):
        await sample_kvstore.special_call.stopped()

    with trio.fail_after(0.1):
        await test_state.stopped.wait()

    assert test_state.terminated_with is None
    assert test_state.did_raise is None


@pytest.mark.trio
async def test_kvstore_call_failure(test_state):
    with pytest.raises(t2.GenServerExited):
        await sample_kvstore.special_call.failure()

    with trio.fail_after(0.1):
        await test_state.stopped.wait()

    assert isinstance(test_state.terminated_with, RuntimeError)
    assert test_state.did_raise is test_state.terminated_with


@pytest.mark.trio
async def test_kvstore_cast_normal(test_state):
    await sample_kvstore.special_cast.normal()

    with trio.fail_after(0.1):
        await test_state.casted.wait()


@pytest.mark.trio
async def tests_kvstore_cast_stop(test_state):
    await sample_kvstore.special_cast.stop()

    with trio.fail_after(0.1):
        await test_state.stopped.wait()

    assert test_state.terminated_with is None
    assert test_state.did_raise is None


@pytest.mark.trio
async def test_kvstore_cast_fail(test_state):
    await sample_kvstore.special_cast.fail()

    with trio.fail_after(0.1):
        await test_state.stopped.wait()

    assert isinstance(test_state.terminated_with, NotImplementedError)
    assert test_state.did_raise is test_state.terminated_with


@pytest.mark.trio
async def test_kvstore_info_stop(test_state):
    await sample_kvstore.special_info.stop()

    with trio.fail_after(0.1):
        await test_state.stopped.wait()

    assert test_state.terminated_with is None
    assert test_state.did_raise is None


@pytest.mark.trio
async def test_kvstore_info_fail(test_state):
    await sample_kvstore.special_info.fail()

    with trio.fail_after(0.1):
        await test_state.stopped.wait()

    assert isinstance(test_state.terminated_with, RuntimeError)
    assert test_state.did_raise is test_state.terminated_with


@pytest.mark.trio
async def test_kvstore_info_matched(test_state):
    await sample_kvstore.special_info.matched('foo')

    with trio.fail_after(0.1):
        await test_state.info.wait()

    assert test_state.info_val == 'foo'


@pytest.mark.trio
async def test_kvstore_info_no_match(test_state):
    await sample_kvstore.special_info.no_match('foo')

    with trio.fail_after(0.1):
        await test_state.info.wait()

    assert test_state.info_val is None
    assert len(test_state.unknown_info) == 1
    assert test_state.unknown_info[0] == ('special_info_no_match', 'foo')
