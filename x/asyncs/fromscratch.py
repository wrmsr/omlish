"""
https://jacobpadilla.com/articles/recreating-asyncio
"""
from queue import Queue
import time
import typing as ta


event_loop = Queue()


def _sleep(seconds: float | int) -> ta.Generator[None, None, None]:
    start_time = time.time()
    while time.time() - start_time < seconds:
        yield


async def sleep(seconds: float):
    task = create_task(_sleep(seconds))
    return await task


class Task:
    def __init__(self, generator) -> None:
        self.iter = generator
        self.finished = False

    def done(self):
        return self.finished

    def __await__(self):
        while not self.finished:
            yield self


def create_task(generator) -> Task:
    task = Task(generator)
    event_loop.put(task)

    return task


def run(main: ta.Awaitable) -> None:
    event_loop.put(Task(main))

    while not event_loop.empty():
        task = event_loop.get()
        try:
            task.iter.send(None)
        except StopIteration:
            task.finished = True
        else:
            event_loop.put(task)


def _main():
    async def task1():
        for _ in range(2):
            print('Task 1')
            await sleep(1)

    async def task2():
        for _ in range(3):
            print('Task 2')
            await sleep(0)

    async def a_main():
        one = create_task(task1())
        two = create_task(task2())

        await one
        await two

        print('done')

    run(a_main())


if __name__ == '__main__':
    _main()
