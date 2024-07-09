import trio

from . import triotp2 as t2


async def fn0():
    for i in range(4):
        await trio.sleep(2)
        print(f'fn0: {i=}')
    raise Exception('fn0')


async def fn1():
    for i in range(3):
        await trio.sleep(3)
        print(f'fn1: {i=}')
    raise Exception('fn1')


async def start():
   children = [
     t2.ChildSpec(
       id='fn0',
       task=fn0,
       args=[],
     ),
     t2.ChildSpec(
       id='fn1',
       task=fn1,
       args=[],
     ),
   ]
   opts = t2.SupervisorOptions()
   await t2.supervisor_start(children, opts)


if __name__ == '__main__':
    trio.run(start)
