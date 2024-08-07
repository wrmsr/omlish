import pytest
import trio

from omlish.testing.pytest import assert_raises_star

from .. import triotp2 as t2


class Producer:
    def __init__(self, mbox):
        self.mbox = mbox

    async def __call__(self, message):
        await t2.mailboxes().send(self.mbox, message)


class Consumer:
    def __init__(
            self,
            mbox,
            timeout=None,
            with_on_timeout=True,
    ) -> None:
        super().__init__()
        self.mbox = mbox
        self.timeout = timeout
        self.with_on_timeout = with_on_timeout

        self.received_message = None
        self.timed_out = False

    async def on_timeout(self):
        self.timed_out = True
        return None

    async def __call__(self, task_status=trio.TASK_STATUS_IGNORED):
        async with t2.mailboxes().open(self.mbox) as mid:
            task_status.started(mid)

            cb = self.on_timeout if self.with_on_timeout else None
            self.received_message = await t2.mailboxes().receive(
                mid,
                timeout=self.timeout,
                on_timeout=cb,
            )


@pytest.mark.trio
async def test_receive_no_timeout(mailbox_env):
    producer = Producer("pytest")
    consumer = Consumer("pytest")

    async with trio.open_nursery() as nursery:
        await nursery.start(consumer)
        nursery.start_soon(producer, "foo")

    assert not consumer.timed_out
    assert consumer.received_message == "foo"


@pytest.mark.trio
async def test_receive_on_timeout(mailbox_env):
    consumer = Consumer("pytest", timeout=0.01)

    async with trio.open_nursery() as nursery:
        await nursery.start(consumer)

    assert consumer.timed_out
    assert consumer.received_message is None


@pytest.mark.trio
async def test_receive_too_slow(mailbox_env):
    consumer = Consumer("pytest", timeout=0.01, with_on_timeout=False)

    with assert_raises_star(trio.TooSlowError):
        async with trio.open_nursery() as nursery:
            await nursery.start(consumer)

    assert not consumer.timed_out
    assert consumer.received_message is None


@pytest.mark.trio
async def test_no_mailbox(mailbox_env):
    producer = Producer("pytest")

    with pytest.raises(t2.MailboxDoesNotExist):
        await producer("foo")

    with pytest.raises(t2.MailboxDoesNotExist):
        await t2.mailboxes().receive("pytest")


@pytest.mark.trio
async def test_direct(mailbox_env):
    consumer = Consumer(None)

    async with trio.open_nursery() as nursery:
        mid = await nursery.start(consumer)
        producer = Producer(mid)
        nursery.start_soon(producer, "foo")

    assert not consumer.timed_out
    assert consumer.received_message == "foo"


@pytest.mark.trio
async def test_register(mailbox_env):
    consumer = Consumer("pytest")

    with pytest.raises(t2.MailboxDoesNotExist):
        t2.mailboxes().register("not-found", "pytest")

    with assert_raises_star(t2.NameAlreadyExist):
        async with trio.open_nursery() as nursery:
            await nursery.start(consumer)
            await nursery.start(consumer)


@pytest.mark.trio
async def test_unregister(mailbox_env):
    consumer = Consumer("pytest")
    producer = Producer("pytest")

    with assert_raises_star(t2.MailboxDoesNotExist):
        async with trio.open_nursery() as nursery:
            await nursery.start(consumer)

            t2.mailboxes().unregister("pytest")

            with pytest.raises(t2.NameDoesNotExist):
                t2.mailboxes().unregister("pytest")

            nursery.start_soon(producer, "foo")


@pytest.mark.trio
async def test_destroy_unknown(mailbox_env):
    with pytest.raises(t2.MailboxDoesNotExist):
        await t2.mailboxes().destroy("not-found")
