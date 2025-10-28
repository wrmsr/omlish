import asyncio
import itertools


async def mock_sensor(name):
    for n in itertools.count():
        await asyncio.sleep(0.1)
        if n == 1 and name == 'b':  # 'presence detection'
            yield 'PRESENT'
        elif n == 3 and name == 'a':  # inject a simple bug
            print('oops, raising RuntimeError')
            raise RuntimeError
        else:
            yield f'{name}-{n}'  # non-presence sensor data


async def move_elements_to_queue(ait, queue):
    async for obj in ait:
        await queue.put(obj)


async def combined_iterators(*aits):
    """Combine async iterators by starting N tasks, each of
    which move elements from one iterable to a shared queue."""
    q = asyncio.Queue(maxsize=2)
    async with asyncio.TaskGroup() as tg:
        for ait in aits:
            tg.create_task(move_elements_to_queue(ait, q))
        while True:
            yield await q.get()


async def turn_on_lights_when_someone_gets_home():
    combined = combined_iterators(mock_sensor('a'), mock_sensor('b'))
    async for event in combined:
        print(event)
        if event == 'PRESENT':
            break
    print('main task sleeping for a bit')
    await asyncio.sleep(1)  # do some other operation


asyncio.run(turn_on_lights_when_someone_gets_home())
