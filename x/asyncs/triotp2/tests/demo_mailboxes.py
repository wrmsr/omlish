from .. import triotp2 as t2

import trio


async def consumer(task_status=trio.TASK_STATUS_IGNORED):
    async with t2.mailboxes().open('foo') as mid:
        task_status.started(None)

        message = await t2.mailboxes().receive(mid)
        print(message)


async def producer():
    await t2.mailboxes().send('foo', 'Hello World!')


async def main():
    t2.init_mailboxes()

    async with trio.open_nursery() as nursery:
        await nursery.start(consumer)
        nursery.start_soon(producer)


if __name__ == '__main__':
    trio.run(main)
