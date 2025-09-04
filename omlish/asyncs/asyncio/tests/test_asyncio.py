import asyncio


def test_asyncio():
    def hello_world(loop):
        print('Hello World')
        loop.stop()

    loop = asyncio.new_event_loop()

    # Schedule a call to hello_world()
    loop.call_soon(hello_world, loop)

    # Blocking call interrupted by loop.stop()
    try:
        loop.run_forever()
    finally:
        loop.close()


def test_create_task():
    async def worker(name: str, delay: float) -> str:
        await asyncio.sleep(delay)
        return f'{name} finished after {delay} seconds'

    async def main():
        # Create tasks
        task1 = asyncio.create_task(worker('task1', 1))
        task2 = asyncio.create_task(worker('task2', 2))

        # Await results
        result1 = await task1
        result2 = await task2

        return result1, result2

    results = asyncio.run(main())

    assert results == (
        'task1 finished after 1 seconds',
        'task2 finished after 2 seconds',
    )
