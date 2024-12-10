import asyncio
import traceback


def dump_running_tasks(loop):
    tasks = asyncio.all_tasks(loop)

    print("Running tasks:")
    for task in tasks:
        print(task)

        stack = task.get_stack()

        if stack:
            print("".join(traceback.format_stack(stack[-1])))


async def main():
    # Create some tasks
    task1 = asyncio.create_task(asyncio.sleep(1))
    task2 = asyncio.create_task(asyncio.sleep(2))

    async def dump():
        # Dump the tasks
        dump_running_tasks(asyncio.get_running_loop())

    await dump()

    # Wait for tasks to complete
    await asyncio.gather(task1, task2)


if __name__ == "__main__":
    asyncio.run(main())
